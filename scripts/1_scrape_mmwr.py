"""
EpiBrief-MMWR-LM Dataset Construction
Script 1: MMWR Article Scraper

This script downloads CDC MMWR articles using URL enumeration.
It probes canonical MMWR URL patterns across all publication series.

Author: Bryan Tegomoh
Date: 2025-10-28
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import logging

# Ensure logs directory exists before configuring logging
Path("../logs").mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/scrape_mmwr.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://www.cdc.gov"
START_YEAR = 2015  # Full production range
END_YEAR = 2025
DELAY_BETWEEN_REQUESTS = 1.5  # seconds (respectful to CDC servers)
DELAY_ON_404 = 0.5  # shorter delay for missing articles
RAW_DATA_DIR = Path("../raw")

# Enumeration bounds (heuristic but robust to template changes)
MAX_ISSUES_PER_YEAR = 60  # weekly issues plus supplements/early releases
MAX_ARTICLES_PER_ISSUE = 12  # typical a1..a6, allow slack for special issues
MAX_EARLY_RELEASES = 3  # e1, e2, e3 (rarely more)
CONSECUTIVE_404_THRESHOLD = 5  # Stop probing after N consecutive 404s for a1

# HTTP headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


class MMWRScraper:
    """Scraper for CDC MMWR articles using URL enumeration"""

    def __init__(self, start_year=START_YEAR, end_year=END_YEAR):
        self.start_year = start_year
        self.end_year = end_year
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.stats = {
            'years_scraped': 0,
            'articles_found': 0,
            'articles_downloaded': 0,
            'articles_skipped': 0,
            'errors': 0,
            'by_series': {'wr': 0, 'ss': 0, 'rr': 0}
        }

    def scrape_year_articles(self, year):
        """
        Enumerate MMWR article URLs for a year by probing canonical patterns.

        Probes four publication series:
        1. Weekly Reports (wr): mm{vol}{issue}a{n}.htm
        2. Early Releases (wr): mm{vol}{issue}e{n}.htm
        3. Surveillance Summaries (ss): ss{vol}{issue}a{n}.htm
        4. Recommendations & Reports (rr): rr{vol}{issue}a{n}.htm

        Args:
            year (int): Year to scrape (e.g., 2024)

        Returns:
            list: List of article dicts with url and metadata
        """
        logger.info(f"Enumerating articles for year {year}")

        # CDC MMWR volume number: volume = year - 1951
        volume = year - 1951
        if volume <= 0:
            logger.warning(f"Invalid volume computed for year {year}")
            return []

        articles = []
        consecutive_404s = 0  # Track consecutive missing a1 articles

        # Enumerate weekly issues (01..60)
        for issue in range(1, MAX_ISSUES_PER_YEAR + 1):
            found_any_for_issue = False

            # 1. Weekly Reports (wr, aN series)
            for a_index in range(1, MAX_ARTICLES_PER_ISSUE + 1):
                article = self._probe_article(volume, issue, 'wr', 'a', a_index, year)
                if article:
                    articles.append(article)
                    found_any_for_issue = True
                    self.stats['by_series']['wr'] += 1
                    consecutive_404s = 0  # Reset on success
                elif a_index == 1:
                    # No a1 found for this issue
                    consecutive_404s += 1
                    break  # No point checking a2, a3, etc.
                else:
                    # Missing a2, a3, etc. - normal, continue to next slot
                    break

            # 2. Early Releases (wr, eN series) - only if we found any aN articles
            if found_any_for_issue:
                for e_index in range(1, MAX_EARLY_RELEASES + 1):
                    article = self._probe_article(volume, issue, 'wr', 'e', e_index, year)
                    if article:
                        articles.append(article)
                        self.stats['by_series']['wr'] += 1
                    else:
                        # Early releases are sparse; stop after first 404
                        break

            # 3. Surveillance Summaries (ss, aN series) - check a1 only
            article = self._probe_article(volume, issue, 'ss', 'a', 1, year)
            if article:
                articles.append(article)
                self.stats['by_series']['ss'] += 1
                # Check for additional ss articles in this issue
                for a_index in range(2, MAX_ARTICLES_PER_ISSUE + 1):
                    article = self._probe_article(volume, issue, 'ss', 'a', a_index, year)
                    if article:
                        articles.append(article)
                        self.stats['by_series']['ss'] += 1
                    else:
                        break

            # 4. Recommendations & Reports (rr, aN series) - check a1 only
            article = self._probe_article(volume, issue, 'rr', 'a', 1, year)
            if article:
                articles.append(article)
                self.stats['by_series']['rr'] += 1
                # Check for additional rr articles in this issue
                for a_index in range(2, MAX_ARTICLES_PER_ISSUE + 1):
                    article = self._probe_article(volume, issue, 'rr', 'a', a_index, year)
                    if article:
                        articles.append(article)
                        self.stats['by_series']['rr'] += 1
                    else:
                        break

            # Early stop heuristic: if many consecutive issues have no a1, break
            if consecutive_404s >= CONSECUTIVE_404_THRESHOLD and issue > 52:
                logger.info(f"Early stop for year {year} at issue {issue} (no articles found)")
                break

        logger.info(f"Found {len(articles)} articles for year {year} "
                   f"(wr: {self.stats['by_series']['wr']}, "
                   f"ss: {self.stats['by_series']['ss']}, "
                   f"rr: {self.stats['by_series']['rr']})")
        return articles

    def _probe_article(self, volume, issue, series, letter, index, year):
        """
        Probe a single MMWR article URL pattern.

        Args:
            volume (int): MMWR volume number
            issue (int): Issue number
            series (str): Publication series ('wr', 'ss', 'rr')
            letter (str): Article letter ('a' for articles, 'e' for early releases)
            index (int): Article index (1, 2, 3...)
            year (int): Publication year

        Returns:
            dict: Article metadata if exists, None otherwise
        """
        # Construct URL based on series
        if series == 'wr':
            # Weekly reports: mm7343a1.htm or mm7343e1.htm
            article_id = f"mm{volume:02d}{issue:02d}{letter}{index}"
            url = f"{BASE_URL}/mmwr/volumes/{volume}/wr/{article_id}.htm"
        elif series == 'ss':
            # Surveillance Summaries: ss7301a1.htm
            article_id = f"ss{volume:02d}{issue:02d}{letter}{index}"
            url = f"{BASE_URL}/mmwr/volumes/{volume}/ss/{article_id}.htm"
        elif series == 'rr':
            # Recommendations & Reports: rr7201a1.htm
            article_id = f"rr{volume:02d}{issue:02d}{letter}{index}"
            url = f"{BASE_URL}/mmwr/volumes/{volume}/rr/{article_id}.htm"
        else:
            logger.error(f"Unknown series: {series}")
            return None

        # Check if URL exists
        exists, status_code = self._url_exists(url)

        if exists:
            logger.debug(f"Found: {article_id}")
            return {
                'url': url,
                'article_id': article_id,
                'series': series,
                'volume': volume,
                'issue': issue,
                'year': year,
                'scraped_date': datetime.now().isoformat()
            }
        else:
            logger.debug(f"Not found: {article_id} (HTTP {status_code})")
            return None

    def _url_exists(self, url, retries=2):
        """
        Check if URL returns HTTP 200.

        Args:
            url (str): URL to check
            retries (int): Number of retries on network errors

        Returns:
            tuple: (exists: bool, status_code: int)
        """
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(url, timeout=20)

                # Check for "Page Not Found" in content (CDC sometimes returns 200 for 404s)
                if resp.status_code == 200 and '<title>Page Not Found' not in resp.text:
                    # Short delay on success
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                    return True, 200

                # 404 or soft-404
                time.sleep(DELAY_ON_404)
                return False, resp.status_code

            except requests.RequestException as e:
                if attempt < retries:
                    # Retry with exponential backoff on network errors
                    time.sleep(1.0 * (2 ** attempt))
                    continue
                logger.warning(f"Network error checking {url}: {e}")
                return False, None

        return False, None

    def download_article(self, article_info, year_dir):
        """
        Download individual article HTML.

        Args:
            article_info (dict): Article metadata including URL
            year_dir (Path): Directory to save the article

        Returns:
            bool: True if successful, False otherwise
        """
        article_id = article_info['article_id']

        # Create filename
        filename = f"{article_id}.html"
        filepath = year_dir / filename

        # Skip if already downloaded
        if filepath.exists():
            logger.debug(f"Skipping {article_id} (already exists)")
            self.stats['articles_skipped'] += 1
            return True

        try:
            # Download article
            logger.info(f"Downloading: {article_id}")
            response = self.session.get(article_info['url'], timeout=30)
            response.raise_for_status()

            # Save HTML
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Save metadata sidecar
            metadata_file = year_dir / f"{article_id}_meta.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(article_info, f, indent=2)

            self.stats['articles_downloaded'] += 1
            logger.info(f"Successfully downloaded: {article_id}")

            # Be polite to CDC servers
            time.sleep(DELAY_BETWEEN_REQUESTS)
            return True

        except requests.RequestException as e:
            logger.error(f"Error downloading {article_id}: {e}")
            self.stats['errors'] += 1
            return False
        except IOError as e:
            logger.error(f"Error saving {article_id}: {e}")
            self.stats['errors'] += 1
            return False

    def scrape_all_years(self):
        """
        Main method to scrape all years in the configured range.
        """
        logger.info(f"Starting MMWR scrape: {self.start_year}-{self.end_year}")
        logger.info(f"Output directory: {RAW_DATA_DIR.absolute()}")

        # Create base directory
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

        all_articles = []

        for year in range(self.start_year, self.end_year + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing year: {year}")
            logger.info(f"{'='*60}")

            # Reset series stats for this year
            self.stats['by_series'] = {'wr': 0, 'ss': 0, 'rr': 0}

            # Create year directory
            year_dir = RAW_DATA_DIR / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)

            # Enumerate articles for this year
            articles = self.scrape_year_articles(year)

            if not articles:
                logger.warning(f"No articles found for {year}")
                continue

            all_articles.extend(articles)
            self.stats['articles_found'] += len(articles)

            # Download each article
            logger.info(f"Downloading {len(articles)} articles from {year}...")
            for article in tqdm(articles, desc=f"Year {year}"):
                self.download_article(article, year_dir)

            self.stats['years_scraped'] += 1

            # Save year index
            year_index_file = year_dir / f"_year_{year}_index.json"
            with open(year_index_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2)

            logger.info(f"Completed year {year}")

        # Save complete index
        self._save_complete_index(all_articles)

        # Print final statistics
        self.print_stats()

        return all_articles

    def _save_complete_index(self, all_articles):
        """Save complete index of all articles."""
        index_file = RAW_DATA_DIR / "_complete_index.json"

        index_data = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'year_range': f"{self.start_year}-{self.end_year}",
                'total_articles': len(all_articles),
                'scraper_version': '2.0.0-enumeration'
            },
            'articles': all_articles,
            'statistics': self.stats
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)

        logger.info(f"Complete index saved to: {index_file}")

    def print_stats(self):
        """Print scraping statistics."""
        logger.info("\n" + "="*60)
        logger.info("SCRAPING STATISTICS")
        logger.info("="*60)
        logger.info(f"Years scraped: {self.stats['years_scraped']}")
        logger.info(f"Articles found: {self.stats['articles_found']}")
        logger.info(f"Articles downloaded: {self.stats['articles_downloaded']}")
        logger.info(f"Articles skipped (already exist): {self.stats['articles_skipped']}")
        logger.info(f"Errors encountered: {self.stats['errors']}")
        logger.info("="*60 + "\n")


def main():
    """Main execution function."""
    print("""
    ==============================================================
           EpiBrief-MMWR-LM Dataset Construction
           CDC MMWR Article Scraper (Enumeration)
    ==============================================================
    """)

    # Initialize scraper
    scraper = MMWRScraper(start_year=START_YEAR, end_year=END_YEAR)

    # Confirm before starting
    print(f"This will enumerate MMWR articles from {START_YEAR} to {END_YEAR}")
    print(f"Publication series: Weekly Reports (wr), Surveillance (ss), Recommendations (rr)")
    print(f"Output directory: {RAW_DATA_DIR.absolute()}")
    print(f"\nDelay between requests: {DELAY_BETWEEN_REQUESTS}s")
    print(f"Estimated articles: 800-1,200+ (varies by year)")

    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Scraping cancelled.")
        return

    # Start scraping
    print("\nStarting enumeration and download...")
    articles = scraper.scrape_all_years()

    print(f"\n✓ Scraping complete!")
    print(f"  Total articles found: {len(articles)}")
    print(f"  Check logs at: logs/scrape_mmwr.log")
    print(f"  Raw data saved to: {RAW_DATA_DIR.absolute()}")
    print(f"\nNext step: Run 2_parse_articles.py to extract structured data")


if __name__ == "__main__":
    main()
