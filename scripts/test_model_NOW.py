"""
Fresh test script for EpiBrief-MMWR-LM - bypassing Python cache issues
"""

import tinker
from tinker import types
from tinker_cookbook import renderers, model_info
from tinker_cookbook.tokenizer_utils import get_tokenizer

print("="*80)
print("   Testing EpiBrief-MMWR-LM")
print("="*80)
print()

# Configuration
TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"
CHECKPOINT_PATH = f"tinker://{TRAINING_RUN_ID}/sampler_weights/final"
MODEL_NAME = "meta-llama/Llama-3.1-8B"

print("Step 1: Loading model components...")
print(f"Checkpoint: {CHECKPOINT_PATH}")
print()

# Create clients
sc = tinker.ServiceClient()
tokenizer = get_tokenizer(MODEL_NAME)
renderer_name = model_info.get_recommended_renderer_name(MODEL_NAME)
renderer = renderers.get_renderer(renderer_name, tokenizer)
sampling_client = sc.create_sampling_client(CHECKPOINT_PATH)

print(f"[OK] Renderer: {renderer_name}")
print("[OK] Model loaded")
print()

# Test prompt
test_prompt = """Based on this MMWR article excerpt, generate an executive summary following CDC format.

Article: Measles Outbreak — Minnesota, 2024

During January-March 2024, 47 measles cases were identified. Among cases, 42 (89%) were unvaccinated, 35 (74%) were children <5 years. Index case had international travel. 18 hospitalizations (38%) occurred; no deaths.

Generate the CDC-style executive summary:"""

print("TEST: Measles outbreak summary generation")
print("-" * 80)
print(test_prompt[:100] + "...")
print("-" * 80)
print()
print("Generating via Tinker API...")
print()

# Create conversation and render to tokens
conversation = [
    renderers.Message(role="user", content=test_prompt)
]

# Render conversation to token IDs using the renderer
tokens, _ = renderer.build_supervised_example(
    conversation,
    renderers.TrainOnWhat.ALL_ASSISTANT_MESSAGES
)

# Convert tokens to ModelInput (what Tinker expects!)
prompt = types.ModelInput.from_ints(tokens.tolist())

# Sampling parameters
sampling_params = types.SamplingParams(
    max_tokens=400,
    temperature=0.7,
    stop=[tokenizer.eos_token]  # Stop at end-of-sequence
)

# Generate (correct signature from docs!)
future = sampling_client.sample(
    prompt=prompt,
    sampling_params=sampling_params,
    num_samples=1
)

result = future.result()

# Debug: print result structure to see what we got
print(f"DEBUG: Result type: {type(result)}")
print(f"DEBUG: Result attributes: {dir(result)}")
print(f"DEBUG: Result: {result}")
print()

# The result is a SampleResponse - check what attributes it actually has
# Based on Tinker docs, it should have a .tokens attribute directly
if hasattr(result, 'tokens'):
    generated_tokens = result.tokens
elif hasattr(result, 'sequences'):
    generated_tokens = result.sequences[0].tokens
else:
    # Try to access first item if it's a list
    generated_tokens = result[0].tokens if isinstance(result, list) else result.tokens

generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

print("="*80)
print("GENERATED OUTPUT:")
print("="*80)
print()
print(generated_text)
print()
print("="*80)
print()
print("SUCCESS! Your trained model works!")
print()
