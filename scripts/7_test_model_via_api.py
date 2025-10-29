"""
Test EpiBrief-MMWR-LM model via Tinker Inference API

This script tests your fine-tuned model WITHOUT downloading weights.
It uses Tinker's inference API to generate CDC-style summaries.
"""

import os
import tinker
from tinker_cookbook.renderers import Message

# Your training run ID
TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"

print("="*80)
print("   Testing EpiBrief-MMWR-LM Model")
print("="*80)
print()

# Check API key
if "TINKER_API_KEY" not in os.environ:
    raise ValueError(
        "TINKER_API_KEY environment variable not set!\n"
        "Set it with: $env:TINKER_API_KEY = 'your-key-here'"
    )

print("Connecting to Tinker API...")
service_client = tinker.ServiceClient()

print("Loading your trained model...")
# Create sampling client from your training run
training_client = service_client.create_training_client_from_run_id(TRAINING_RUN_ID)
sampling_client = training_client.save_weights_and_get_sampling_client(
    name="epibrief-mmwr-lm-test"
)

print(f"✓ Model loaded from: {sampling_client.model_path}")
print()

# Test case: Sample MMWR article excerpt
test_instruction = """Based on this MMWR article excerpt, generate an executive summary following CDC format.

Article Excerpt:
Title: Measles Outbreak Associated with International Travel — Minnesota, 2024

During January–March 2024, the Minnesota Department of Health identified 47 measles cases in a community with low vaccination coverage. Among the 47 cases, 42 (89%) were in unvaccinated individuals, and 35 (74%) were in children aged <5 years. The index case was in a resident who had traveled internationally and was unvaccinated. Secondary transmission occurred in community settings, childcare facilities, and an emergency department. The outbreak resulted in 18 hospitalizations (38%); no deaths occurred. Public health interventions included vaccination campaigns, contact tracing, and community education in multiple languages.

Generate the CDC-style summary with the three standard questions."""

print("="*80)
print("TEST CASE: Measles Outbreak Summary Generation")
print("="*80)
print()
print("INSTRUCTION:")
print(test_instruction[:200] + "...")
print()
print("Generating response...")
print("(This may take 30-60 seconds)")
print()

# Create messages in proper format
messages = [Message(role="user", content=test_instruction)]

try:
    # Generate response using your trained model
    response = sampling_client.generate(
        messages=messages,
        max_tokens=512,
        temperature=0.7,
        top_p=0.9,
        stop_sequences=None
    )

    print("="*80)
    print("GENERATED OUTPUT:")
    print("="*80)
    print()
    print(response.content)
    print()
    print("="*80)
    print()

    # Evaluation prompts
    print("EVALUATION QUESTIONS:")
    print("1. Does it follow CDC's 'What is known/added/implications' format? (Yes/No)")
    print("2. Are the numbers accurate (89%, 74%, 38%)? (Yes/No)")
    print("3. Does it sound like a real CDC MMWR summary? (Yes/No)")
    print("4. Overall quality score (1-5, where 5 is excellent):")
    print()
    print("If you scored 4-5, your model is working well!")
    print("If you scored 2-3, it needs improvement but is on the right track.")
    print("If you scored 1, something went wrong - let me know!")

except Exception as e:
    print(f"Error generating response: {e}")
    print()
    print("This might mean:")
    print("1. The model is still processing (try again in a few minutes)")
    print("2. There's an API issue (check Tinker status)")
    print("3. The training run needs to be finalized")
    print()
    print("Try running this script again in 5-10 minutes.")

print()
print("="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Evaluate the output quality above")
print("2. Try more test cases (modify the test_instruction)")
print("3. Compare to actual CDC MMWR summaries")
print("4. Share results with colleagues for feedback")
print()
print("Want to test more examples? Edit this script and change test_instruction!")
