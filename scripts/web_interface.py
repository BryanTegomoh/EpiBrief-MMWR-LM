"""
Web Interface for EpiBrief-MMWR-LM using Gradio

Run this script and it creates a shareable web interface!
"""

import gradio as gr
import tinker
from tinker import types
from tinker_cookbook import renderers, model_info
from tinker_cookbook.tokenizer_utils import get_tokenizer

# Model configuration
TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"
CHECKPOINT_PATH = f"tinker://{TRAINING_RUN_ID}/sampler_weights/final"
MODEL_NAME = "meta-llama/Llama-3.1-8B"

print("Loading EpiBrief-MMWR-LM model...")
# Initialize model components (only once at startup)
sc = tinker.ServiceClient()
tokenizer = get_tokenizer(MODEL_NAME)
renderer_name = model_info.get_recommended_renderer_name(MODEL_NAME)
renderer = renderers.get_renderer(renderer_name, tokenizer)
sampling_client = sc.create_sampling_client(CHECKPOINT_PATH)
print("Model loaded! Starting web interface...")

def generate_epi_summary(user_input, task_type, max_tokens, temperature):
    """Generate epidemiological analysis based on user input"""

    # Create appropriate prompt based on task type
    task_prompts = {
        "Executive Summary": f"Based on this MMWR article excerpt, generate an executive summary following CDC format with 'What is already known about this topic?', 'What is added by this report?', and 'What are the implications for public health practice?' sections.\n\n{user_input}\n\nGenerate the CDC-style executive summary:",

        "Data Interpretation": f"Interpret the key findings from this epidemiological data:\n\n{user_input}\n\nProvide your epidemiological interpretation:",

        "Public Health Implications": f"Based on these findings, what are the implications for public health practice?\n\n{user_input}\n\nImplications for public health practice:",

        "Outbreak Analysis": f"Analyze this outbreak scenario from an epidemiological perspective:\n\n{user_input}\n\nEpidemiological analysis:"
    }

    prompt_text = task_prompts.get(task_type, user_input)

    # Create conversation
    conversation = [renderers.Message(role="user", content=prompt_text)]

    # Render to tokens
    tokens, _ = renderer.build_supervised_example(
        conversation,
        renderers.TrainOnWhat.ALL_ASSISTANT_MESSAGES
    )

    # Convert to ModelInput
    prompt = types.ModelInput.from_ints(tokens.tolist())

    # Sampling parameters
    sampling_params = types.SamplingParams(
        max_tokens=int(max_tokens),
        temperature=float(temperature),
        stop=[tokenizer.eos_token]
    )

    # Generate
    try:
        future = sampling_client.sample(
            prompt=prompt,
            sampling_params=sampling_params,
            num_samples=1
        )

        result = future.result()

        # Extract tokens and decode
        if hasattr(result, 'tokens'):
            generated_tokens = result.tokens
        elif hasattr(result, 'sequences'):
            generated_tokens = result.sequences[0].tokens
        else:
            generated_tokens = result[0].tokens if isinstance(result, list) else result.tokens

        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

        # Clean up the output (remove prompt if it leaked through)
        if prompt_text in generated_text:
            generated_text = generated_text.replace(prompt_text, "").strip()

        return generated_text

    except Exception as e:
        return f"Error generating response: {str(e)}\n\nPlease try again or adjust parameters."

# Example inputs for demo
examples = [
    [
        "During January-March 2024, 47 measles cases were identified in Minnesota. Among cases, 42 (89%) were unvaccinated, 35 (74%) were children <5 years. Index case had international travel history. 18 hospitalizations (38%) occurred; no deaths.",
        "Executive Summary",
        400,
        0.7
    ],
    [
        "Table: COVID-19 Vaccination Coverage by Age Group\nAge 18-49: 51.2%\nAge 50-64: 68.3%\nAge 65+: 77.3%",
        "Data Interpretation",
        300,
        0.7
    ],
    [
        "A cluster of 12 hepatitis A cases occurred among persons experiencing homelessness in City X during March-April 2024. All cases were unvaccinated. Transmission occurred in shelter settings.",
        "Public Health Implications",
        300,
        0.7
    ]
]

# Create Gradio interface
demo = gr.Interface(
    fn=generate_epi_summary,
    inputs=[
        gr.Textbox(
            label="Input Data (Article excerpt, table, or outbreak scenario)",
            placeholder="Enter MMWR article excerpt, surveillance data, or outbreak description...",
            lines=6
        ),
        gr.Dropdown(
            choices=["Executive Summary", "Data Interpretation", "Public Health Implications", "Outbreak Analysis"],
            label="Task Type",
            value="Executive Summary"
        ),
        gr.Slider(
            minimum=100,
            maximum=800,
            value=400,
            step=50,
            label="Max Output Length (tokens)"
        ),
        gr.Slider(
            minimum=0.0,
            maximum=1.0,
            value=0.7,
            step=0.1,
            label="Temperature (creativity)"
        )
    ],
    outputs=gr.Textbox(
        label="Generated Epidemiological Analysis",
        lines=15
    ),
    title="🦠 EpiBrief-MMWR-LM: AI Epidemiologist",
    description="""
    **Specialized language model trained on 11,632 CDC MMWR training pairs**

    This AI assistant learned epidemiological reasoning from 9 years of CDC's Morbidity and Mortality Weekly Reports (2016-2025).
    It can generate CDC-style summaries, interpret surveillance data, and provide public health recommendations.

    **Developed by:** Bryan Tegomoh, MD, MPH | **Model:** Fine-tuned Llama 3.1 8B (LoRA)
    """,
    examples=examples,
    theme=gr.themes.Soft(),
    analytics_enabled=False
)

# Launch with sharing enabled
if __name__ == "__main__":
    demo.launch(
        share=True,  # Creates public URL you can share!
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
