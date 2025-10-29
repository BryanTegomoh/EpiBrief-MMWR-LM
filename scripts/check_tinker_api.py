"""
Check what Tinker API methods are actually available
"""

import tinker

print("Checking Tinker API...")
print()

# Create service client
service_client = tinker.ServiceClient()

print("Available methods in ServiceClient:")
print("-" * 80)
methods = [m for m in dir(service_client) if not m.startswith('_')]
for method in methods:
    print(f"  - {method}")

print()
print("="*80)
print()

# Check if we can find the training client
print("Trying to find your training run...")
TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"

# Try different approaches
print()
print("Method 1: Check if we can create training client from state...")
try:
    # Your final checkpoint path
    state_path = f"tinker://{TRAINING_RUN_ID}/weights/final"
    training_client = service_client.create_training_client_from_state(state_path)
    print(f"✓ Created training client from state!")

    # Check what methods training_client has
    print()
    print("Training client methods:")
    tc_methods = [m for m in dir(training_client) if not m.startswith('_')]
    for method in tc_methods:
        print(f"  - {method}")

except Exception as e:
    print(f"✗ Error: {e}")

print()
print("="*80)
print()
print("RECOMMENDATION:")
print("Please email Tinker support with this error output:")
print()
print("To: support@thinkingmachines.ai")
print("Subject: API methods missing for inference")
print()
print("Message:")
print('"I successfully trained a model but cannot use it for inference.')
print(f'Training Run ID: {TRAINING_RUN_ID}')
print('The API methods create_training_client_from_run_id and')
print('create_sampling_client_from_tinker_path do not exist.')
print('How do I use my trained model for inference?"')
print()
print("Attach the output from this script.")
