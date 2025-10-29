"""
Download trained LoRA weights from Tinker API

This script downloads your fine-tuned model weights from the Tinker training run.
Run this after training completes successfully.
"""

import os
from pathlib import Path
import tinker

# Your training run ID from Tinker Console
TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"

# Where to save the model
OUTPUT_DIR = Path("../models/epibrief-mmwr-lm-v1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("   EpiBrief-MMWR-LM Model Download")
print("="*80)
print()

# Check API key
if "TINKER_API_KEY" not in os.environ:
    raise ValueError(
        "TINKER_API_KEY environment variable not set!\n"
        "Set it with: $env:TINKER_API_KEY = 'your-key-here'"
    )

print(f"Training Run ID: {TRAINING_RUN_ID}")
print(f"Download location: {OUTPUT_DIR.absolute()}")
print()

# Create service client
print("Connecting to Tinker API...")
service_client = tinker.ServiceClient()

# Create REST client for downloading
print("Creating REST client...")
rest_client = service_client.create_rest_client()

# Option 1: Try downloading from the checkpoint path
print("\nAttempting to download model weights...")
print("(This may take a few minutes depending on model size)")
print()

try:
    # The checkpoint path from your console
    checkpoint_path = f"weights/epoch1_step000050"  # Adjust if needed

    # Download checkpoint archive
    future = rest_client.download_checkpoint_archive_from_tinker_path(
        f"{TRAINING_RUN_ID}/{checkpoint_path}"
    )

    # Get the result
    archive_data = future.result()

    # Save to file
    output_file = OUTPUT_DIR / "epibrief-lora-weights.tar.gz"
    with open(output_file, 'wb') as f:
        f.write(archive_data)

    print(f"✓ Model weights downloaded successfully!")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ File size: {len(archive_data) / (1024*1024):.2f} MB")
    print()
    print("="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Extract the archive:")
    print(f"   tar -xzf {output_file}")
    print()
    print("2. Test your model:")
    print("   python 7_test_model.py")
    print()

except Exception as e:
    print(f"Error downloading from checkpoint path: {e}")
    print()
    print("Trying alternative method...")

    # Alternative: Download using training client
    try:
        training_client = service_client.create_training_client_from_run_id(
            TRAINING_RUN_ID
        )

        # Save weights and get path
        sampling_client = training_client.save_weights_and_get_sampling_client(
            name="epibrief-mmwr-lm-v1"
        )

        print(f"✓ Model saved to Tinker path: {sampling_client.model_path}")
        print()
        print("To use this model for inference, you can:")
        print("1. Use Tinker's inference API (no download needed)")
        print("2. Use the sampling_client directly in Python")
        print()
        print("Model is ready for testing!")

    except Exception as e2:
        print(f"Error with alternative method: {e2}")
        print()
        print("="*80)
        print("MANUAL DOWNLOAD INSTRUCTIONS:")
        print("="*80)
        print("1. Contact Tinker support: support@thinkingmachines.ai")
        print(f"2. Provide your Training Run ID: {TRAINING_RUN_ID}")
        print("3. Request checkpoint download link")
        print()
        print("OR use Tinker's inference API directly (no download needed)")
        print("See documentation: https://tinker-docs.thinkingmachines.ai/inference")
