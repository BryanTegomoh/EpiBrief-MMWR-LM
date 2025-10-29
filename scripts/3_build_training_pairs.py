"""
EpiBrief-MMWR-LM Dataset Construction
Script 3: Training Pairs Generator

This script converts parsed MMWR articles into instruction/response pairs
for supervised fine-tuning of language models.

Author: Bryan Tegomoh
Date: 2025-10-28
License: MIT
"""

import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/build_training_pairs.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
PARSED_DATA_DIR = Path("../parsed_json")
TRAINING_DATA_DIR = Path("../training_data")


class TrainingPairGenerator:
    """Generate instruction/response training pairs from parsed MMWR articles"""

    def __init__(self):
        self.stats = {
            'articles_processed': 0,
            'total_pairs_generated': 0,
            'pairs_by_type': {},
            'skipped_articles': 0
        }

    def generate_pairs_from_article(self, article_data):
        """
        Generate multiple training pairs from a single article

        Args:
            article_data (dict): Parsed article data

        Returns:
            list: List of training pair dictionaries
        """
        pairs = []

        # Extract key fields
        title = article_data.get('title', '')
        summary = article_data.get('summary', {})
        sections = article_data.get('sections', {})
        metadata = article_data.get('metadata', {})
        category = article_data.get('category', '')

        # Skip if essential data missing
        if not title:
            logger.warning(f"Skipping article {article_data.get('id')} - no title")
            self.stats['skipped_articles'] += 1
            return []

        # Generate different types of training pairs
        pairs.extend(self._generate_summary_pairs(title, summary, sections, metadata))
        pairs.extend(self._generate_methods_pairs(title, sections, metadata))
        pairs.extend(self._generate_results_pairs(title, sections, metadata))
        pairs.extend(self._generate_implications_pairs(title, summary, sections, metadata))
        pairs.extend(self._generate_case_definition_pairs(title, sections, metadata))
        pairs.extend(self._generate_recommendations_pairs(title, sections, metadata))
        pairs.extend(self._generate_key_facts_pairs(title, sections, summary, metadata))

        return pairs

    def _generate_summary_pairs(self, title, summary, sections, metadata):
        """Generate executive summary training pairs"""
        pairs = []

        # Type 1: From structured summary box
        if isinstance(summary, dict) and summary.get('what_is_added'):
            pairs.append({
                "instruction": "Summarize the key findings of this CDC MMWR report in 2-3 sentences for a state health director, using CDC MMWR style.",
                "input": f"Title: {title}\n\nWhat is added by this report: {summary.get('what_is_added', '')}",
                "output": summary.get('what_is_added', ''),
                "pair_type": "executive_summary"
            })

        # Type 2: From abstract + results
        if sections.get('abstract') and sections.get('results'):
            abstract_snippet = sections['abstract'][:500]
            results_snippet = sections['results'][:500]

            pairs.append({
                "instruction": "Write a brief executive summary of this outbreak investigation for public health leadership.",
                "input": f"Title: {title}\n\nAbstract: {abstract_snippet}\n\nResults: {results_snippet}",
                "output": sections['abstract'],
                "pair_type": "executive_summary"
            })

        # Type 3: Full summary with context
        if isinstance(summary, dict) and all(k in summary for k in ['what_is_known', 'what_is_added', 'implications']):
            full_summary = f"What is already known: {summary['what_is_known']}\n\n"
            full_summary += f"What is added by this report: {summary['what_is_added']}\n\n"
            full_summary += f"Implications for public health practice: {summary['implications']}"

            pairs.append({
                "instruction": "Provide a structured summary of this MMWR report following CDC format: What is already known, What is added, and Implications for public health practice.",
                "input": f"Title: {title}\n\nReport category: {metadata.get('report_type', 'surveillance report')}",
                "output": full_summary,
                "pair_type": "structured_summary"
            })

        self._update_pair_stats('summary', len(pairs))
        return pairs

    def _generate_methods_pairs(self, title, sections, metadata):
        """Generate surveillance methods training pairs"""
        pairs = []

        methods_text = sections.get('methods')
        if not methods_text:
            return []

        # Type 1: Full methods description
        pairs.append({
            "instruction": "Describe the surveillance and investigation methods used in this CDC MMWR report.",
            "input": f"Title: {title}\n\nThis is a {metadata.get('report_type', 'surveillance')} report about {', '.join(metadata.get('pathogens', ['a public health issue']))} in {', '.join(metadata.get('jurisdictions', ['the United States'])[:2])}.",
            "output": methods_text,
            "pair_type": "methods_description"
        })

        # Type 2: Case definition extraction (if present)
        if 'case' in methods_text.lower() and 'defin' in methods_text.lower():
            case_def_snippet = self._extract_case_definition(methods_text)
            if case_def_snippet:
                pairs.append({
                    "instruction": f"What case definition was used for surveillance in this report?",
                    "input": f"Title: {title}\n\nPathogen: {', '.join(metadata.get('pathogens', ['unknown']))}",
                    "output": case_def_snippet,
                    "pair_type": "case_definition"
                })

        # Type 3: Data sources
        if 'data' in methods_text.lower() and 'source' in methods_text.lower():
            pairs.append({
                "instruction": "What data sources were used in this surveillance report?",
                "input": f"Title: {title}",
                "output": methods_text,
                "pair_type": "data_sources"
            })

        self._update_pair_stats('methods', len(pairs))
        return pairs

    def _generate_results_pairs(self, title, sections, metadata):
        """Generate results/findings training pairs"""
        pairs = []

        results_text = sections.get('results')
        if not results_text:
            return []

        # Type 1: Key findings summary
        results_snippet = results_text[:600]  # First 600 chars
        pairs.append({
            "instruction": "Summarize the main results and findings from this public health investigation.",
            "input": f"Title: {title}\n\nContext: This report examines {', '.join(metadata.get('pathogens', ['a public health issue']))}.",
            "output": results_snippet,
            "pair_type": "results_summary"
        })

        # Type 2: Case counts and epidemiology (if numbers present)
        if re.search(r'\d+\s*(cases?|patients?|persons?|individuals?)', results_text, re.IGNORECASE):
            pairs.append({
                "instruction": "What were the case counts and key epidemiologic characteristics identified in this investigation?",
                "input": f"Title: {title}",
                "output": results_text,
                "pair_type": "epidemiologic_findings"
            })

        self._update_pair_stats('results', len(pairs))
        return pairs

    def _generate_implications_pairs(self, title, summary, sections, metadata):
        """Generate public health implications training pairs"""
        pairs = []

        # Source 1: Structured summary
        if isinstance(summary, dict) and summary.get('implications'):
            pairs.append({
                "instruction": "What are the public health implications of these findings?",
                "input": f"Title: {title}\n\nKey findings: {summary.get('what_is_added', '')[:300]}",
                "output": summary['implications'],
                "pair_type": "public_health_implications"
            })

        # Source 2: Discussion section
        discussion_text = sections.get('discussion')
        if discussion_text:
            # Extract last paragraph (often contains implications)
            paragraphs = discussion_text.split('\n\n')
            if len(paragraphs) > 0:
                last_para = paragraphs[-1]
                if len(last_para) > 100:  # Substantial paragraph
                    pairs.append({
                        "instruction": "Based on these findings, what are the implications for public health practice?",
                        "input": f"Title: {title}\n\nFindings: {sections.get('results', '')[:400]}",
                        "output": last_para,
                        "pair_type": "implications_from_discussion"
                    })

        # Source 3: Conclusions
        conclusions_text = sections.get('conclusions')
        if conclusions_text:
            pairs.append({
                "instruction": "What conclusions and recommendations emerge from this investigation?",
                "input": f"Title: {title}",
                "output": conclusions_text,
                "pair_type": "conclusions"
            })

        self._update_pair_stats('implications', len(pairs))
        return pairs

    def _generate_case_definition_pairs(self, title, sections, metadata):
        """Generate case definition training pairs"""
        pairs = []

        methods_text = sections.get('methods', '')
        full_text = sections.get('abstract', '') + ' ' + methods_text

        # Look for case definitions
        case_def = self._extract_case_definition(full_text)

        if case_def:
            pathogen = metadata.get('pathogens', ['the disease'])[0] if metadata.get('pathogens') else 'the disease'
            jurisdiction = metadata.get('jurisdictions', ['the jurisdiction'])[0] if metadata.get('jurisdictions') else 'the jurisdiction'

            pairs.append({
                "instruction": f"Define a confirmed case of {pathogen} for public health surveillance purposes, following CDC guidelines.",
                "input": f"Context: This is from an outbreak investigation in {jurisdiction}.",
                "output": case_def,
                "pair_type": "case_definition"
            })

        self._update_pair_stats('case_definition', len(pairs))
        return pairs

    def _generate_recommendations_pairs(self, title, sections, metadata):
        """Generate recommendations/actions training pairs"""
        pairs = []

        # Source 1: From discussion
        discussion = sections.get('discussion', '')
        if discussion and ('recommend' in discussion.lower() or 'should' in discussion.lower()):
            recommendations_snippet = self._extract_recommendations(discussion)
            if recommendations_snippet:
                pairs.append({
                    "instruction": "What actions and recommendations should public health departments implement based on these findings?",
                    "input": f"Title: {title}\n\nContext: {metadata.get('report_type', 'investigation')}",
                    "output": recommendations_snippet,
                    "pair_type": "recommendations"
                })

        # Source 2: From conclusions
        conclusions = sections.get('conclusions', '')
        if conclusions:
            pairs.append({
                "instruction": "What are the key recommended actions for public health practice?",
                "input": f"Title: {title}",
                "output": conclusions,
                "pair_type": "recommended_actions"
            })

        self._update_pair_stats('recommendations', len(pairs))
        return pairs

    def _generate_key_facts_pairs(self, title, sections, summary, metadata):
        """Generate quick facts/key points training pairs"""
        pairs = []

        # Extract key numerical facts
        results = sections.get('results', '')
        abstract = sections.get('abstract', '')

        combined_text = abstract + ' ' + results

        # Look for key statistics
        case_count_match = re.search(r'(\d+)\s*(cases?|patients?|persons?)', combined_text, re.IGNORECASE)
        if case_count_match:
            context_window = combined_text[max(0, case_count_match.start()-200):case_count_match.end()+200]

            pairs.append({
                "instruction": "State the total number of cases, the time frame, and the key control measures implemented.",
                "input": f"Title: {title}",
                "output": context_window.strip(),
                "pair_type": "key_statistics"
            })

        # Outbreak timeline
        if metadata.get('report_type') == 'outbreak_investigation':
            timeline_snippet = self._extract_timeline(combined_text)
            if timeline_snippet:
                pairs.append({
                    "instruction": "Describe the outbreak timeline and key dates.",
                    "input": f"Title: {title}",
                    "output": timeline_snippet,
                    "pair_type": "outbreak_timeline"
                })

        self._update_pair_stats('key_facts', len(pairs))
        return pairs

    def _extract_case_definition(self, text):
        """Extract case definition from text"""
        # Look for patterns like "A confirmed case was defined as..."
        patterns = [
            r'((?:confirmed|probable|suspect|suspected)\s+case\s+(?:was\s+)?defined\s+as[^.]+\.)',
            r'(case\s+definition[^.]+\.)',
            r'(cases?\s+were\s+confirmed\s+by[^.]+\.)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    def _extract_recommendations(self, text):
        """Extract recommendations from text"""
        # Look for paragraphs containing recommendations
        sentences = text.split('.')
        rec_sentences = []

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ['recommend', 'should', 'must', 'need to', 'important to']):
                rec_sentences.append(sentence.strip() + '.')

        if rec_sentences:
            return ' '.join(rec_sentences[:5])  # First 5 recommendation sentences

        return None

    def _extract_timeline(self, text):
        """Extract timeline information from text"""
        # Look for date patterns and temporal phrases
        date_pattern = r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:–\d{1,2})?,?\s+\d{4})'

        matches = re.findall(date_pattern, text, re.IGNORECASE)

        if len(matches) >= 2:
            # Find context around dates
            first_date = matches[0]
            last_date = matches[-1]

            timeline_text = f"The investigation occurred from {first_date} to {last_date}."

            # Add more context if available
            for match in matches:
                idx = text.lower().find(match.lower())
                if idx != -1:
                    context = text[max(0, idx-100):min(len(text), idx+100)]
                    timeline_text += f" {context}"

            return timeline_text[:500]  # Limit length

        return None

    def _update_pair_stats(self, pair_type, count):
        """Update statistics for pair generation"""
        if pair_type not in self.stats['pairs_by_type']:
            self.stats['pairs_by_type'][pair_type] = 0
        self.stats['pairs_by_type'][pair_type] += count
        self.stats['total_pairs_generated'] += count

    def generate_all_training_pairs(self):
        """Generate training pairs from all parsed articles"""
        logger.info("Starting training pair generation...")

        # Create output directory
        TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Load all parsed articles
        parsed_files = list(PARSED_DATA_DIR.glob("*.json"))
        parsed_files = [f for f in parsed_files if not f.name.startswith('_')]  # Skip index files

        logger.info(f"Found {len(parsed_files)} parsed articles")

        all_pairs = []

        for parsed_file in tqdm(parsed_files, desc="Generating training pairs"):
            try:
                with open(parsed_file, 'r', encoding='utf-8') as f:
                    article_data = json.load(f)

                pairs = self.generate_pairs_from_article(article_data)
                all_pairs.extend(pairs)

                self.stats['articles_processed'] += 1

            except Exception as e:
                logger.error(f"Error processing {parsed_file}: {e}")

        # Save training pairs as JSONL
        self._save_training_pairs(all_pairs)

        # Print statistics
        self.print_stats()

        return all_pairs

    def _save_training_pairs(self, all_pairs):
        """Save training pairs in JSONL format"""
        # Main training file
        training_file = TRAINING_DATA_DIR / "epibrief_training.jsonl"

        with open(training_file, 'w', encoding='utf-8') as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')

        logger.info(f"Training pairs saved to: {training_file}")

        # Also save as regular JSON for inspection
        training_json = TRAINING_DATA_DIR / "epibrief_training.json"
        with open(training_json, 'w', encoding='utf-8') as f:
            json.dump(all_pairs, f, indent=2, ensure_ascii=False)

        # Save metadata
        metadata = {
            'created': datetime.now().isoformat(),
            'total_pairs': len(all_pairs),
            'statistics': self.stats,
            'generator_version': '1.0.0'
        }

        metadata_file = TRAINING_DATA_DIR / "_training_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def print_stats(self):
        """Print generation statistics"""
        logger.info("\n" + "="*60)
        logger.info("TRAINING PAIR GENERATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Articles processed: {self.stats['articles_processed']}")
        logger.info(f"Total training pairs: {self.stats['total_pairs_generated']}")
        logger.info(f"Skipped articles: {self.stats['skipped_articles']}")

        logger.info("\nPairs by type:")
        for pair_type, count in sorted(self.stats['pairs_by_type'].items()):
            logger.info(f"  {pair_type}: {count}")

        if self.stats['articles_processed'] > 0:
            avg_pairs = self.stats['total_pairs_generated'] / self.stats['articles_processed']
            logger.info(f"\nAverage pairs per article: {avg_pairs:.1f}")

        logger.info("="*60 + "\n")


def main():
    """Main execution function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         EpiBrief-MMWR-LM Dataset Construction            ║
    ║           Training Pairs Generator                       ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Initialize generator
    generator = TrainingPairGenerator()

    # Confirm before starting
    print(f"This will generate instruction/response training pairs")
    print(f"Input directory: {PARSED_DATA_DIR.absolute()}")
    print(f"Output directory: {TRAINING_DATA_DIR.absolute()}")

    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Generation cancelled.")
        return

    # Start generation
    print("\nGenerating training pairs...")
    pairs = generator.generate_all_training_pairs()

    print(f"\n✓ Training pair generation complete!")
    print(f"  Total pairs generated: {generator.stats['total_pairs_generated']}")
    print(f"  Check logs at: logs/build_training_pairs.log")
    print(f"  Training data saved to: {TRAINING_DATA_DIR.absolute()}")
    print(f"\nNext step: Run 4_validate_dataset.py to validate data quality")


if __name__ == "__main__":
    main()
