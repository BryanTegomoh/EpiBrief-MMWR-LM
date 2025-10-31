"""
Re-download trained LoRA weights from Tinker API (WORKING VERSION)
"""

import os
from pathlib import Path
import tinker
import requests

# Your training run ID
TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"
CHECKPOINT_PATH = "weights/epoch1_step000050"

# Where to save
OUTPUT_DIR = Path("models/epibrief-mmwr-lm-v1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("   EpiBrief-MMWR-LM Model Download (Fixed)")
print("="*80)
print(f"\nTraining Run ID: {TRAINING_RUN_ID}")
print(f"Checkpoint: {CHECKPOINT_PATH}")
print(f"Output: {OUTPUT_DIR.absolute()}\n")

# Connect to Tinker
print("Connecting to Tinker API...")
service_client = tinker.ServiceClient()
rest_client = service_client.create_rest_client()

# Get download URL
print("Getting checkpoint download URL...")
tinker_path = f"tinker://{TRAINING_RUN_ID}/sampler_weights/epoch3_final"
future = rest_client.get_checkpoint_archive_url_from_tinker_path(tinker_path)
response = future.result()
download_url = response.url

print(f"Download URL obtained: {download_url[:60] if len(download_url) > 60 else download_url}...")

# Download the file
print("\nDownloading model weights (this may take a few minutes)...")
response = requests.get(download_url, stream=True)
response.raise_for_status()

output_file = OUTPUT_DIR / "weights.tar"
total_size = int(response.headers.get('content-length', 0))

with open(output_file, 'wb') as f:
    downloaded = 0
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                percent = (downloaded / total_size) * 100
                print(f"\rProgress: {percent:.1f}% ({downloaded/(1024*1024):.1f} MB)", end='')

print(f"\n\n✓ Model weights downloaded successfully!")
print(f"✓ Saved to: {output_file}")
print(f"✓ File size: {downloaded / (1024*1024):.2f} MB")

# Extract the archive
print("\nExtracting weights...")
import tarfile
with tarfile.open(output_file, 'r') as tar:
    tar.extractall(OUTPUT_DIR)

print("✓ Extraction complete!")

# List extracted files
print("\nExtracted files:")
for item in OUTPUT_DIR.rglob("*"):
    if item.is_file():
        print(f"  {item.relative_to(OUTPUT_DIR)}")

print("\n" + "="*80)
print("SUCCESS! Model ready for upload to HuggingFace")
print("="*80)
