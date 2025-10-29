"""
Use your trained EpiBrief model from Tinker

Your model is saved at:
tinker://dee4e48d-4e45-42d9-9371-a997dac170fd/sampler_weights/final
"""

import os
import json
import tinker
from tinker_cookbook import model_info
from tinker_cookbook.tokenizer_utils import get_tokenizer

TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"
MODEL_NAME = "meta-llama/Llama-3.1-8B"

print("="*80)
print("   Testing Your Trained EpiBrief-MMWR-LM Model")
print("="*80)
print()

# Check API key
if "TINKER_API_KEY" not in os.environ:
    raise ValueError(
        "TINKER_API_KEY environment variable not set!\n"
        "Set it with: $env:TINKER_API_KEY = 'your-key-here'"
    )

print("Step 1: Connecting to Tinker...")
service_client = tinker.ServiceClient()

print("Step 2: Creating sampling client from your trained model...")
print(f"        Model path: tinker://{TRAINING_RUN_ID}/sampler_weights/final")

# Create sampling client directly from the saved path
sampling_client = service_client.create_sampling_client_from_tinker_path(
    f"tinker://{TRAINING_RUN_ID}/sampler_weights/final"
)

print("✓ Model loaded successfully!")
print()

# Test case
test_prompt = """Based on this MMWR article excerpt, generate an executive summary following CDC format.

Article: Measles Outbreak Associated with International Travel — Minnesota, 2024

During January–March 2024, the Minnesota Department of Health identified 47 measles cases in a community with low vaccination coverage. Among the 47 cases, 42 (89%) were in unvaccinated individuals, and 35 (74%) were in children aged <5 years. The index case was in a resident who had traveled internationally and was unvaccinated. Secondary transmission occurred in community settings, childcare facilities, and an emergency department. The outbreak resulted in 18 hospitalizations (38%); no deaths occurred. Public health interventions included vaccination campaigns, contact tracing, and community education in multiple languages.

Generate the CDC-style summary with "What is known", "What is added", and "Implications" sections."""

print("="*80)
print("TEST: Generating CDC-Style Measles Outbreak Summary")
print("="*80)
print()
print("Sending prompt to your trained model...")
print("(This may take 30-60 seconds)")
print()

# Get tokenizer and renderer
tokenizer = get_tokenizer(MODEL_NAME)
renderer_name = model_info.get_recommended_renderer_name(MODEL_NAME)

from tinker_cookbook import renderers
renderer = renderers.get_renderer(renderer_name, tokenizer)

# Build prompt using renderer
model_input = renderer.build_generation_prompt(
    [{"role": "user", "content": test_prompt}],
    role="assistant"
)

# Sample from model
response_ids = sampling_client.sample(
    model_input=model_input,
    temperature=0.7,
    top_p=0.9,
    max_tokens=512
)

# Parse response
response_message, complete = renderer.parse_response(response_ids)

print("="*80)
print("GENERATED OUTPUT:")
print("="*80)
print()
print(response_message["content"])
print()
print("="*80)
print()

if complete:
    print("✓ Generation completed successfully!")
else:
    print("⚠ Generation may be truncated (hit max tokens)")

print()
print("="*80)
print("EVALUATION:")
print("="*80)
print()
print("Review the output above and answer:")
print("1. Does it follow CDC's 'What is known/added/implications' format?")
print("2. Are the numbers accurate (89%, 74%, 38%)?")
print("3. Does it sound professional and CDC-like?")
print("4. Would you use this in actual work? (Yes/No)")
print()
print("If mostly YES → Your model works! 🎉")
print("If mostly NO → May need more training or different parameters")
print()
print("="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Test on more examples (edit test_prompt above)")
print("2. Compare to actual CDC MMWR summaries")
print("3. Get feedback from colleagues")
print("4. Document your results")
print("5. Share on Twitter/LinkedIn!")
print()
