"""
EpiBrief-MMWR-LM Dataset Splitter
Split training pairs into train/validation sets for Tinker fine-tuning
"""

import json
import random
from pathlib import Path

# Configuration
INPUT_FILE = Path("../training_data/training_pairs.jsonl")
TRAIN_FILE = Path("../training_data/train.jsonl")
VAL_FILE = Path("../training_data/val.jsonl")
VAL_SPLIT = 0.1  # 10% validation
RANDOM_SEED = 42

print("="*70)
print("   EpiBrief-MMWR-LM Dataset Splitter")
print("="*70 + "\n")

# Load training pairs
print(f"Loading training pairs from: {INPUT_FILE}")
pairs = []
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        pairs.append(json.loads(line))

print(f"Total pairs loaded: {len(pairs)}")

# Shuffle with fixed seed for reproducibility
random.seed(RANDOM_SEED)
random.shuffle(pairs)

# Split
split_idx = int((1 - VAL_SPLIT) * len(pairs))
train_pairs = pairs[:split_idx]
val_pairs = pairs[split_idx:]

print(f"\nSplit:")
print(f"  Train: {len(train_pairs)} pairs ({100*(1-VAL_SPLIT):.0f}%)")
print(f"  Val:   {len(val_pairs)} pairs ({100*VAL_SPLIT:.0f}%)")

# Verify pair type distribution
train_types = {}
val_types = {}

for pair in train_pairs:
    pt = pair['pair_type']
    train_types[pt] = train_types.get(pt, 0) + 1

for pair in val_pairs:
    pt = pair['pair_type']
    val_types[pt] = val_types.get(pt, 0) + 1

print(f"\nTrain distribution:")
for pt, count in sorted(train_types.items()):
    print(f"  {pt:30s}: {count:5d}")

print(f"\nVal distribution:")
for pt, count in sorted(val_types.items()):
    print(f"  {pt:30s}: {count:5d}")

# Save splits
print(f"\nSaving train split to: {TRAIN_FILE}")
with open(TRAIN_FILE, 'w', encoding='utf-8') as f:
    for pair in train_pairs:
        f.write(json.dumps(pair) + '\n')

print(f"Saving val split to: {VAL_FILE}")
with open(VAL_FILE, 'w', encoding='utf-8') as f:
    for pair in val_pairs:
        f.write(json.dumps(pair) + '\n')

print("\n" + "="*70)
print("✓ Dataset split complete!")
print("✓ Ready for Tinker fine-tuning")
print("="*70 + "\n")
