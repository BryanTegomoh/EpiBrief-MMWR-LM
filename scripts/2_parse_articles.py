"""
EpiBrief-MMWR-LM Dataset Construction
Script 2: Article Parser

This script parses downloaded MMWR HTML files and extracts structured data
including metadata, sections, and content for training data generation.

Author: Bryan Tegomoh
Date: 2025-10-28
License: MIT
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/parse_articles.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
RAW_DATA_DIR = Path("../raw")
PARSED_DATA_DIR = Path("../parsed_json")

# Common pathogens for automatic detection
PATHOGENS = [
    'influenza', 'covid-19', 'coronavirus', 'sars-cov-2', 'measles', 'mumps',
    'rubella', 'hepatitis', 'hiv', 'tuberculosis', 'malaria', 'dengue',
    'zika', 'ebola', 'norovirus', 'rotavirus', 'salmonella', 'e. coli',
    'legionella', 'listeria', 'mpox', 'monkeypox', 'pertussis', 'meningitis',
    'pneumonia', 'rsv', 'respiratory syncytial virus', 'west nile virus',
    'lyme disease', 'rabies', 'anthrax', 'plague', 'smallpox', 'typhoid',
    'cholera', 'yellow fever', 'chikungunya', 'hantavirus', 'histoplasmosis'
]

# US states and territories for jurisdiction detection
US_JURISDICTIONS = [
    'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
    'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
    'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
    'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
    'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
    'new hampshire', 'new jersey', 'new mexico', 'new york',
    'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon',
    'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
    'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
    'west virginia', 'wisconsin', 'wyoming', 'district of columbia',
    'puerto rico', 'guam', 'u.s. virgin islands', 'american samoa',
    'northern mariana islands', 'united states', 'u.s.'
]


class MMWRArticleParser:
    """Parser for MMWR article HTML files"""

    def __init__(self):
        self.stats = {
            'total_files': 0,
            'successfully_parsed': 0,
            'parsing_errors': 0,
            'missing_sections': 0
        }

    def parse_html_file(self, html_path):
        """
        Parse a single MMWR HTML file

        Args:
            html_path (Path): Path to HTML file

        Returns:
            dict: Structured article data
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract all components
            article_data = {
                'id': html_path.stem,
                'source_file': str(html_path),
                'parsed_date': datetime.now().isoformat(),
            }

            # Extract metadata
            article_data.update(self._extract_metadata(soup))

            # Extract summary box
            article_data['summary'] = self._extract_summary(soup)

            # Extract main sections
            article_data['sections'] = self._extract_sections(soup)

            # Extract full text
            article_data['full_text'] = self._extract_full_text(soup)

            # Automatic classification
            article_data['metadata'] = self._classify_article(article_data)

            return article_data

        except Exception as e:
            logger.error(f"Error parsing {html_path}: {e}")
            self.stats['parsing_errors'] += 1
            return None

    def _extract_metadata(self, soup):
        """Extract metadata from HTML meta tags"""
        metadata = {}

        # Essential metadata from meta tags
        meta_mappings = {
            'title': 'citation_title',
            'category': 'citation_categories',
            'volume': 'citation_volume',
            'doi': 'citation_doi',
            'publication_date': 'citation_publication_date',
            'description': 'Description'
        }

        for key, meta_name in meta_mappings.items():
            meta_tag = soup.find('meta', {'name': meta_name})
            if meta_tag and meta_tag.get('content'):
                metadata[key] = meta_tag['content'].strip()
            else:
                metadata[key] = None

        # Extract authors (multiple meta tags)
        author_tags = soup.find_all('meta', {'name': 'citation_author'})
        metadata['authors'] = [tag['content'].strip() for tag in author_tags if tag.get('content')]

        # Extract CDC-specific metadata
        first_published = soup.find('meta', {'property': 'cdc:first_published'})
        if first_published:
            metadata['first_published'] = first_published['content']

        last_updated = soup.find('meta', {'property': 'cdc:last_updated'})
        if last_updated:
            metadata['last_updated'] = last_updated['content']

        # Extract from visible content if meta tags missing
        if not metadata.get('title'):
            h1 = soup.find('h1')
            if h1:
                metadata['title'] = h1.get_text(strip=True)

        # Extract dateline (volume/issue info)
        dateline = soup.select_one('div.dateline p')
        if dateline:
            dateline_text = dateline.get_text(strip=True)
            metadata['dateline'] = dateline_text

            # Parse issue number from dateline
            issue_match = re.search(r'(\d+)\((\d+)\)', dateline_text)
            if issue_match:
                metadata['issue'] = issue_match.group(2)

        # Extract PDF URL
        pdf_link = soup.select_one('a[href*="/pdfs/"]')
        if pdf_link:
            pdf_url = pdf_link['href']
            if pdf_url.startswith('/'):
                pdf_url = 'https://www.cdc.gov' + pdf_url
            metadata['pdf_url'] = pdf_url

        return metadata

    def _extract_summary(self, soup):
        """
        Extract the summary box (gray background) with
        "What is already known", "What is added", "What are the implications"
        """
        summary_box = soup.select_one('div.bg-gray-l2')

        if not summary_box:
            return None

        summary_text = summary_box.get_text(separator='\n', strip=True)

        # Try to parse structured summary
        summary = {}

        # Pattern 1: "What is already known about this topic?"
        known_match = re.search(
            r'What is already known.*?\?(.*?)(?=What is added|$)',
            summary_text,
            re.DOTALL | re.IGNORECASE
        )
        if known_match:
            summary['what_is_known'] = known_match.group(1).strip()

        # Pattern 2: "What is added by this report?"
        added_match = re.search(
            r'What is added.*?\?(.*?)(?=What are the implications|$)',
            summary_text,
            re.DOTALL | re.IGNORECASE
        )
        if added_match:
            summary['what_is_added'] = added_match.group(1).strip()

        # Pattern 3: "What are the implications for public health practice?"
        implications_match = re.search(
            r'What are the implications.*?\?(.*?)$',
            summary_text,
            re.DOTALL | re.IGNORECASE
        )
        if implications_match:
            summary['implications'] = implications_match.group(1).strip()

        # If structured parsing failed, just store full text
        if not summary:
            summary['full_summary'] = summary_text

        return summary

    def _extract_sections(self, soup):
        """Extract main article sections using anchor IDs"""
        sections = {}

        # Standard section IDs
        section_ids = [
            'abstract',
            'introduction',
            'methods',
            'results',
            'discussion',
            'conclusions',
            'acknowledgments',
            'references'
        ]

        # Alternative section names for "Notes from the Field"
        alternative_ids = [
            'investigationandoutcomes',
            'preliminaryconclusionsandactions'
        ]

        all_section_ids = section_ids + alternative_ids

        for section_id in all_section_ids:
            content = self._get_section_content(soup, section_id)
            if content:
                # Normalize section name (remove "and" variations)
                normalized_name = section_id.lower().replace('and', '_')
                sections[normalized_name] = content

        # If no sections found, this might be a different article type
        if not sections:
            self.stats['missing_sections'] += 1
            logger.warning(f"No standard sections found in article")

        return sections

    def _get_section_content(self, soup, section_id):
        """
        Extract content for a specific section by anchor ID

        Args:
            soup: BeautifulSoup object
            section_id: Section anchor ID (e.g., 'abstract', 'methods')

        Returns:
            str: Section content or None if not found
        """
        # Find the anchor tag
        anchor = soup.find('a', {'id': section_id})
        if not anchor:
            # Try with capital first letter
            anchor = soup.find('a', {'id': section_id.capitalize()})

        if not anchor:
            return None

        # Get parent heading
        heading = anchor.parent
        if not heading:
            return None

        # Collect all content until next section heading
        content_parts = []
        current = heading.find_next_sibling()

        while current:
            # Stop at next h2 (section heading)
            if current.name == 'div' and current.find('h2'):
                break

            # Collect text content
            text = current.get_text(strip=True)
            if text:
                content_parts.append(text)

            current = current.find_next_sibling()

        return '\n\n'.join(content_parts) if content_parts else None

    def _extract_full_text(self, soup):
        """Extract complete article text"""
        content_div = soup.select_one('div.syndicate')

        if not content_div:
            logger.warning("Could not find main content div")
            return None

        # Remove references section (too verbose)
        refs = content_div.find('a', {'id': 'References'})
        if refs and refs.parent:
            # Remove everything from References onward
            for element in refs.parent.find_all_next():
                element.decompose()

        # Get clean text
        full_text = content_div.get_text(separator='\n', strip=True)

        return full_text

    def _classify_article(self, article_data):
        """
        Automatically classify article attributes

        Returns:
            dict: Classification metadata
        """
        classification = {}

        full_text_lower = article_data.get('full_text', '').lower()
        title_lower = article_data.get('title', '').lower()

        # Detect pathogen
        detected_pathogens = []
        for pathogen in PATHOGENS:
            if pathogen in full_text_lower or pathogen in title_lower:
                detected_pathogens.append(pathogen)

        classification['pathogens'] = detected_pathogens[:3]  # Top 3

        # Detect jurisdiction
        detected_jurisdictions = []
        for jurisdiction in US_JURISDICTIONS:
            if jurisdiction in full_text_lower or jurisdiction in title_lower:
                detected_jurisdictions.append(jurisdiction)

        classification['jurisdictions'] = list(set(detected_jurisdictions))[:5]  # Top 5 unique

        # Classify report type
        category = article_data.get('category', '').lower()
        title = article_data.get('title', '').lower()

        if 'notes from the field' in title or 'notes from the field' in category:
            report_type = 'notes_from_field'
        elif 'quickstats' in title or 'quickstats' in category:
            report_type = 'quickstats'
        elif 'surveillance' in category:
            report_type = 'surveillance_summary'
        elif 'recommendations' in category or 'recommendations' in title:
            report_type = 'recommendations'
        elif 'outbreak' in full_text_lower[:1000]:  # Check first 1000 chars
            report_type = 'outbreak_investigation'
        else:
            report_type = 'full_report'

        classification['report_type'] = report_type

        # Extract topics/keywords
        topics = []

        # Common epidemiologic terms
        topic_keywords = [
            'outbreak', 'surveillance', 'vaccination', 'immunization',
            'screening', 'prevention', 'treatment', 'diagnosis',
            'epidemic', 'pandemic', 'endemic', 'transmission',
            'mortality', 'morbidity', 'incidence', 'prevalence',
            'case investigation', 'contact tracing', 'quarantine',
            'isolation', 'public health', 'health department'
        ]

        for keyword in topic_keywords:
            if keyword in full_text_lower:
                topics.append(keyword)

        classification['topics'] = list(set(topics))[:10]  # Top 10 unique

        return classification

    def parse_all_articles(self):
        """Parse all downloaded articles"""
        logger.info("Starting article parsing...")

        # Create output directory
        PARSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Find all HTML files
        html_files = list(RAW_DATA_DIR.rglob("*.html"))
        logger.info(f"Found {len(html_files)} HTML files to parse")

        self.stats['total_files'] = len(html_files)

        parsed_articles = []

        for html_file in tqdm(html_files, desc="Parsing articles"):
            article_data = self.parse_html_file(html_file)

            if article_data:
                # Save individual JSON file
                output_file = PARSED_DATA_DIR / f"{article_data['id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, indent=2, ensure_ascii=False)

                parsed_articles.append(article_data)
                self.stats['successfully_parsed'] += 1

        # Save complete parsed dataset
        self._save_complete_dataset(parsed_articles)

        # Print statistics
        self.print_stats()

        return parsed_articles

    def _save_complete_dataset(self, parsed_articles):
        """Save complete parsed dataset"""
        dataset_file = PARSED_DATA_DIR / "_complete_parsed_dataset.json"

        dataset = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'total_articles': len(parsed_articles),
                'parser_version': '1.0.0'
            },
            'articles': parsed_articles,
            'statistics': self.stats
        }

        with open(dataset_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        logger.info(f"Complete dataset saved to: {dataset_file}")

    def print_stats(self):
        """Print parsing statistics"""
        logger.info("\n" + "="*60)
        logger.info("PARSING STATISTICS")
        logger.info("="*60)
        logger.info(f"Total files processed: {self.stats['total_files']}")
        logger.info(f"Successfully parsed: {self.stats['successfully_parsed']}")
        logger.info(f"Parsing errors: {self.stats['parsing_errors']}")
        logger.info(f"Articles with missing sections: {self.stats['missing_sections']}")

        if self.stats['total_files'] > 0:
            success_rate = (self.stats['successfully_parsed'] / self.stats['total_files']) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")

        logger.info("="*60 + "\n")


def main():
    """Main execution function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         EpiBrief-MMWR-LM Dataset Construction            ║
    ║              Article Structure Parser                    ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Initialize parser
    parser = MMWRArticleParser()

    # Confirm before starting
    print(f"This will parse all downloaded MMWR articles")
    print(f"Input directory: {RAW_DATA_DIR.absolute()}")
    print(f"Output directory: {PARSED_DATA_DIR.absolute()}")

    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Parsing cancelled.")
        return

    # Start parsing
    print("\nStarting parse...")
    articles = parser.parse_all_articles()

    print(f"\n✓ Parsing complete!")
    print(f"  Successfully parsed: {parser.stats['successfully_parsed']} articles")
    print(f"  Check logs at: logs/parse_articles.log")
    print(f"  Parsed data saved to: {PARSED_DATA_DIR.absolute()}")
    print(f"\nNext step: Run 3_build_training_pairs.py to generate training data")


if __name__ == "__main__":
    main()
