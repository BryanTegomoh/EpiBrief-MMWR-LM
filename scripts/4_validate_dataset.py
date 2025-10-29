"""
EpiBrief-MMWR-LM Dataset Construction
Script 4: Dataset Validator

This script validates the quality and completeness of the training dataset,
checks for duplicates, analyzes distribution, and generates statistics.

Author: Bryan Tegomoh
Date: 2025-10-28
License: MIT
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/validate_dataset.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
TRAINING_DATA_DIR = Path("../training_data")
PARSED_DATA_DIR = Path("../parsed_json")


class DatasetValidator:
    """Validate training dataset quality and completeness"""

    def __init__(self):
        self.stats = {
            'total_pairs': 0,
            'valid_pairs': 0,
            'invalid_pairs': 0,
            'duplicate_pairs': 0,
            'issues': []
        }
        self.pair_type_counts = Counter()
        self.year_distribution = Counter()
        self.pathogen_distribution = Counter()
        self.jurisdiction_distribution = Counter()

    def load_training_data(self):
        """Load training pairs from JSONL file"""
        training_file = TRAINING_DATA_DIR / "epibrief_training.jsonl"

        if not training_file.exists():
            logger.error(f"Training file not found: {training_file}")
            return []

        logger.info(f"Loading training data from: {training_file}")

        pairs = []
        with open(training_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    pair = json.loads(line)
                    pairs.append(pair)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error on line {line_num}: {e}")
                    self.stats['issues'].append(f"Line {line_num}: Invalid JSON")

        self.stats['total_pairs'] = len(pairs)
        logger.info(f"Loaded {len(pairs)} training pairs")

        return pairs

    def validate_pair(self, pair, pair_index):
        """
        Validate a single training pair

        Args:
            pair (dict): Training pair
            pair_index (int): Index in dataset

        Returns:
            bool: True if valid, False otherwise
        """
        is_valid = True
        issues = []

        # Check required fields
        required_fields = ['instruction', 'input', 'output', 'pair_type']
        for field in required_fields:
            if field not in pair:
                issues.append(f"Missing field: {field}")
                is_valid = False

        if not is_valid:
            self.stats['issues'].append(f"Pair {pair_index}: {', '.join(issues)}")
            return False

        # Check field types
        if not isinstance(pair['instruction'], str):
            issues.append("instruction must be string")
            is_valid = False

        if not isinstance(pair['input'], str):
            issues.append("input must be string")
            is_valid = False

        if not isinstance(pair['output'], str):
            issues.append("output must be string")
            is_valid = False

        # Check field lengths
        if len(pair['instruction']) < 10:
            issues.append("instruction too short")
            is_valid = False

        if len(pair['output']) < 20:
            issues.append("output too short")
            is_valid = False

        # Check for empty strings
        if not pair['instruction'].strip():
            issues.append("instruction is empty")
            is_valid = False

        if not pair['output'].strip():
            issues.append("output is empty")
            is_valid = False

        # Check output length (not too long, not too short)
        output_len = len(pair['output'])
        if output_len < 20:
            issues.append(f"output too short ({output_len} chars)")
            is_valid = False
        elif output_len > 5000:
            issues.append(f"output very long ({output_len} chars) - may need truncation")
            # Don't mark as invalid, just warning

        if issues:
            self.stats['issues'].append(f"Pair {pair_index}: {', '.join(issues)}")

        return is_valid

    def check_duplicates(self, pairs):
        """Check for duplicate training pairs"""
        logger.info("Checking for duplicates...")

        seen_outputs = {}
        duplicates = []

        for i, pair in enumerate(pairs):
            output = pair.get('output', '').strip()

            if output in seen_outputs:
                duplicates.append({
                    'index': i,
                    'duplicate_of': seen_outputs[output],
                    'output_preview': output[:100]
                })
                self.stats['duplicate_pairs'] += 1
            else:
                seen_outputs[output] = i

        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate pairs")
            for dup in duplicates[:10]:  # Show first 10
                logger.warning(f"  Pair {dup['index']} duplicates pair {dup['duplicate_of']}")

        return duplicates

    def analyze_distribution(self, pairs):
        """Analyze distribution of pairs across types, years, topics"""
        logger.info("Analyzing dataset distribution...")

        # Pair type distribution
        for pair in pairs:
            pair_type = pair.get('pair_type', 'unknown')
            self.pair_type_counts[pair_type] += 1

        # Load parsed articles for metadata analysis
        parsed_files = list(PARSED_DATA_DIR.glob("*.json"))
        parsed_files = [f for f in parsed_files if not f.name.startswith('_')]

        for parsed_file in parsed_files:
            try:
                with open(parsed_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)

                # Year distribution
                pub_date = article.get('publication_date', '')
                if pub_date:
                    year = pub_date[:4] if len(pub_date) >= 4 else 'unknown'
                    self.year_distribution[year] += 1

                # Pathogen distribution
                metadata = article.get('metadata', {})
                for pathogen in metadata.get('pathogens', []):
                    self.pathogen_distribution[pathogen] += 1

                # Jurisdiction distribution
                for jurisdiction in metadata.get('jurisdictions', []):
                    self.jurisdiction_distribution[jurisdiction] += 1

            except Exception as e:
                logger.error(f"Error reading {parsed_file}: {e}")

    def validate_all(self):
        """Validate entire training dataset"""
        logger.info("Starting dataset validation...")

        # Load training pairs
        pairs = self.load_training_data()

        if not pairs:
            logger.error("No training pairs found!")
            return

        # Validate each pair
        logger.info("Validating individual pairs...")
        for i, pair in enumerate(pairs):
            if self.validate_pair(pair, i):
                self.stats['valid_pairs'] += 1
            else:
                self.stats['invalid_pairs'] += 1

        # Check for duplicates
        duplicates = self.check_duplicates(pairs)

        # Analyze distribution
        self.analyze_distribution(pairs)

        # Generate report
        self.generate_report(pairs, duplicates)

    def generate_report(self, pairs, duplicates):
        """Generate validation report"""
        report = {
            'validation_date': datetime.now().isoformat(),
            'dataset_summary': {
                'total_pairs': self.stats['total_pairs'],
                'valid_pairs': self.stats['valid_pairs'],
                'invalid_pairs': self.stats['invalid_pairs'],
                'duplicate_pairs': self.stats['duplicate_pairs'],
                'validity_rate': (self.stats['valid_pairs'] / self.stats['total_pairs'] * 100) if self.stats['total_pairs'] > 0 else 0
            },
            'pair_type_distribution': dict(self.pair_type_counts.most_common()),
            'temporal_distribution': dict(self.year_distribution.most_common()),
            'pathogen_distribution': dict(self.pathogen_distribution.most_common(20)),
            'jurisdiction_distribution': dict(self.jurisdiction_distribution.most_common(20)),
            'issues': self.stats['issues'][:100],  # First 100 issues
            'duplicates': duplicates[:50]  # First 50 duplicates
        }

        # Save report
        report_file = TRAINING_DATA_DIR / "_validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report saved to: {report_file}")

        # Generate human-readable summary
        self._generate_summary_report(report)

    def _generate_summary_report(self, report):
        """Generate human-readable validation summary"""
        summary_file = TRAINING_DATA_DIR / "_validation_summary.txt"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("EpiBrief-MMWR-LM DATASET VALIDATION REPORT\n")
            f.write("="*70 + "\n\n")

            f.write(f"Validation Date: {report['validation_date']}\n\n")

            # Dataset Summary
            f.write("DATASET SUMMARY\n")
            f.write("-" * 70 + "\n")
            summary = report['dataset_summary']
            f.write(f"Total training pairs: {summary['total_pairs']:,}\n")
            f.write(f"Valid pairs: {summary['valid_pairs']:,}\n")
            f.write(f"Invalid pairs: {summary['invalid_pairs']:,}\n")
            f.write(f"Duplicate pairs: {summary['duplicate_pairs']:,}\n")
            f.write(f"Validity rate: {summary['validity_rate']:.1f}%\n\n")

            # Pair Type Distribution
            f.write("PAIR TYPE DISTRIBUTION\n")
            f.write("-" * 70 + "\n")
            for pair_type, count in report['pair_type_distribution'].items():
                percentage = (count / summary['total_pairs'] * 100) if summary['total_pairs'] > 0 else 0
                f.write(f"{pair_type:30s} {count:6,} ({percentage:5.1f}%)\n")
            f.write("\n")

            # Temporal Distribution
            f.write("TEMPORAL DISTRIBUTION (by publication year)\n")
            f.write("-" * 70 + "\n")
            for year, count in sorted(report['temporal_distribution'].items()):
                f.write(f"{year}: {count:4,} articles\n")
            f.write("\n")

            # Top Pathogens
            f.write("TOP PATHOGENS COVERED (Top 15)\n")
            f.write("-" * 70 + "\n")
            for pathogen, count in list(report['pathogen_distribution'].items())[:15]:
                f.write(f"{pathogen:30s} {count:4,} articles\n")
            f.write("\n")

            # Top Jurisdictions
            f.write("TOP JURISDICTIONS (Top 15)\n")
            f.write("-" * 70 + "\n")
            for jurisdiction, count in list(report['jurisdiction_distribution'].items())[:15]:
                f.write(f"{jurisdiction:30s} {count:4,} articles\n")
            f.write("\n")

            # Issues Summary
            if report['issues']:
                f.write("ISSUES FOUND (first 20)\n")
                f.write("-" * 70 + "\n")
                for issue in report['issues'][:20]:
                    f.write(f"- {issue}\n")
                f.write("\n")

            # Quality Assessment
            f.write("QUALITY ASSESSMENT\n")
            f.write("-" * 70 + "\n")

            validity_rate = summary['validity_rate']
            if validity_rate >= 95:
                quality = "EXCELLENT"
            elif validity_rate >= 90:
                quality = "GOOD"
            elif validity_rate >= 80:
                quality = "ACCEPTABLE"
            else:
                quality = "NEEDS IMPROVEMENT"

            f.write(f"Overall Quality: {quality}\n\n")

            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")

            if summary['invalid_pairs'] > 0:
                f.write(f"- Review and fix {summary['invalid_pairs']} invalid pairs\n")

            if summary['duplicate_pairs'] > 10:
                f.write(f"- Consider removing {summary['duplicate_pairs']} duplicate pairs\n")

            # Check temporal balance
            years = report['temporal_distribution']
            if len(years) > 0:
                year_counts = list(years.values())
                max_year_count = max(year_counts)
                min_year_count = min(year_counts)
                if max_year_count > min_year_count * 3:
                    f.write("- Dataset shows temporal imbalance; consider balancing across years\n")

            # Check pair type balance
            pair_types = report['pair_type_distribution']
            if pair_types:
                type_counts = list(pair_types.values())
                max_type_count = max(type_counts)
                min_type_count = min(type_counts)
                if max_type_count > min_type_count * 10:
                    f.write("- Consider more balanced distribution across pair types\n")

            if summary['validity_rate'] >= 95 and summary['total_pairs'] >= 2000:
                f.write("- Dataset is ready for fine-tuning!\n")

            f.write("\n" + "="*70 + "\n")

        logger.info(f"Summary report saved to: {summary_file}")

        # Print to console
        print("\n")
        with open(summary_file, 'r', encoding='utf-8') as f:
            print(f.read())

    def print_stats(self):
        """Print validation statistics"""
        logger.info("\n" + "="*60)
        logger.info("VALIDATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Total pairs: {self.stats['total_pairs']}")
        logger.info(f"Valid pairs: {self.stats['valid_pairs']}")
        logger.info(f"Invalid pairs: {self.stats['invalid_pairs']}")
        logger.info(f"Duplicate pairs: {self.stats['duplicate_pairs']}")

        if self.stats['total_pairs'] > 0:
            validity_rate = (self.stats['valid_pairs'] / self.stats['total_pairs']) * 100
            logger.info(f"Validity rate: {validity_rate:.1f}%")

        logger.info(f"\nTop 5 pair types:")
        for pair_type, count in self.pair_type_counts.most_common(5):
            logger.info(f"  {pair_type}: {count}")

        logger.info("="*60 + "\n")


def main():
    """Main execution function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         EpiBrief-MMWR-LM Dataset Construction            ║
    ║              Dataset Validator                           ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Initialize validator
    validator = DatasetValidator()

    # Confirm before starting
    print(f"This will validate the training dataset")
    print(f"Training data directory: {TRAINING_DATA_DIR.absolute()}")

    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Validation cancelled.")
        return

    # Start validation
    print("\nValidating dataset...")
    validator.validate_all()

    print(f"\n✓ Validation complete!")
    print(f"  Check logs at: logs/validate_dataset.log")
    print(f"  Validation report: {TRAINING_DATA_DIR.absolute()}/_validation_report.json")
    print(f"  Summary report: {TRAINING_DATA_DIR.absolute()}/_validation_summary.txt")
    print(f"\nPhase 1 Complete! Your dataset is ready for fine-tuning.")


if __name__ == "__main__":
    main()
