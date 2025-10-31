"""
EpiBrief-MMWR-LM: CDC-Style Epidemiological Reasoning AI
Hugging Face Space Demo

Author: Bryan Tegomoh, MD, MPH
Model: Fine-tuned Llama 3.1 8B on 11,632 CDC MMWR training pairs
"""

import gradio as gr
import os

# Check if running on Hugging Face Spaces
IS_SPACES = os.environ.get("SPACE_ID") is not None

# Try to import tinker (only works if API key is set)
HAS_TINKER = False
try:
    if not IS_SPACES:  # Only try importing locally, not on HF Spaces
        import tinker
        from tinker import types
        from tinker_cookbook import renderers, model_info
        from tinker_cookbook.tokenizer_utils import get_tokenizer
        HAS_TINKER = True
except ImportError:
    pass

if HAS_TINKER:

    TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"
    CHECKPOINT_PATH = f"tinker://{TRAINING_RUN_ID}/sampler_weights/final"
    MODEL_NAME = "meta-llama/Llama-3.1-8B"

    # Initialize model (cached)
    @gr.cache(
        cache_examples=False,
    )
    def load_model():
        sc = tinker.ServiceClient()
        tokenizer = get_tokenizer(MODEL_NAME)
        renderer_name = model_info.get_recommended_renderer_name(MODEL_NAME)
        renderer = renderers.get_renderer(renderer_name, tokenizer)
        sampling_client = sc.create_sampling_client(CHECKPOINT_PATH)
        return tokenizer, renderer, sampling_client

    tokenizer, renderer, sampling_client = load_model()

    def generate_epi_summary(user_input, task_type, max_tokens, temperature):
        """Generate epidemiological analysis"""

        task_prompts = {
            "Executive Summary": f"Based on this MMWR article excerpt, generate an executive summary following CDC format with 'What is already known about this topic?', 'What is added by this report?', and 'What are the implications for public health practice?' sections.\n\n{user_input}\n\nGenerate the CDC-style executive summary:",
            "Data Interpretation": f"Interpret the key findings from this epidemiological data:\n\n{user_input}\n\nProvide your epidemiological interpretation:",
            "Public Health Implications": f"Based on these findings, what are the implications for public health practice?\n\n{user_input}\n\nImplications for public health practice:",
            "Outbreak Analysis": f"Analyze this outbreak scenario from an epidemiological perspective:\n\n{user_input}\n\nEpidemiological analysis:"
        }

        prompt_text = task_prompts.get(task_type, user_input)

        conversation = [renderers.Message(role="user", content=prompt_text)]
        tokens, _ = renderer.build_supervised_example(
            conversation,
            renderers.TrainOnWhat.ALL_ASSISTANT_MESSAGES
        )

        prompt = types.ModelInput.from_ints(tokens.tolist())
        sampling_params = types.SamplingParams(
            max_tokens=int(max_tokens),
            temperature=float(temperature),
            stop=[tokenizer.eos_token]
        )

        try:
            future = sampling_client.sample(
                prompt=prompt,
                sampling_params=sampling_params,
                num_samples=1
            )
            result = future.result()

            if hasattr(result, 'tokens'):
                generated_tokens = result.tokens
            else:
                generated_tokens = result[0].tokens if isinstance(result, list) else result.tokens

            generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

            if prompt_text in generated_text:
                generated_text = generated_text.replace(prompt_text, "").strip()

            return generated_text

        except Exception as e:
            return f"Error: {str(e)}\n\nPlease try again or contact bryan.tegomoh@berkeley.edu"

else:
    # Demo mode when Tinker isn't available
    def generate_epi_summary(user_input, task_type, max_tokens, temperature):
        return """
**DEMO MODE** (Model not loaded - configure Tinker API credentials to enable)

This is what the model would generate for your input. In production:
- Analyzes outbreak scenarios with CDC-level reasoning
- Interprets surveillance data quantitatively
- Generates evidence-based public health recommendations

**Example output for measles outbreak:**
'Measles is a highly contagious vaccine-preventable viral disease. Increasing U.S.
measles cases have been driven by unvaccinated persons who are exposed while traveling
internationally. U.S. health officials should coordinate response activities to prevent
and limit the spread, assess and improve vaccination coverage, and ensure MMR vaccination
for all eligible children and adults...'

Contact: bryan.tegomoh@berkeley.edu
"""

# Example inputs
examples = [
    [
        "During January-March 2024, 47 measles cases were identified in Minnesota. Among cases, 42 (89%) were unvaccinated, 35 (74%) were children <5 years. Index case had international travel. 18 hospitalizations (38%); no deaths.",
        "Executive Summary",
        400,
        0.7
    ],
    [
        "Table: COVID-19 Vaccination Coverage by Age\nAge 18-49: 51.2%\nAge 50-64: 68.3%\nAge 65+: 77.3%",
        "Data Interpretation",
        300,
        0.7
    ],
]

# Gradio Interface
demo = gr.Interface(
    fn=generate_epi_summary,
    inputs=[
        gr.Textbox(
            label="📊 Input Data",
            placeholder="Enter MMWR article excerpt, surveillance data, or outbreak scenario...",
            lines=8
        ),
        gr.Dropdown(
            choices=["Executive Summary", "Data Interpretation", "Public Health Implications", "Outbreak Analysis"],
            label="🎯 Task Type",
            value="Executive Summary"
        ),
        gr.Slider(100, 800, 400, step=50, label="📏 Max Length"),
        gr.Slider(0.0, 1.0, 0.7, step=0.1, label="🌡️ Temperature"),
    ],
    outputs=gr.Textbox(label="🦠 Generated Analysis", lines=15),
    title="EpiBrief-MMWR-LM: AI Epidemiologist",
    description="""
**Specialized AI trained on 11,632 CDC MMWR training pairs (2016-2025)**

This model learned epidemiological reasoning from 9 years of CDC's Morbidity and Mortality Weekly Reports.
It generates CDC-style outbreak analyses, interprets surveillance data, and provides evidence-based public health recommendations.

🏥 **Developed by:** Bryan Tegomoh, MD, MPH
🤖 **Model:** Llama 3.1 8B fine-tuned with LoRA
📊 **Training:** 11,632 instruction-response pairs (85% quantitative focus)
🔬 **Use Cases:** Outbreak investigation, surveillance analysis, public health communication

📄 [GitHub](https://github.com/BryanTegomoh/EpiBrief-MMWR-LM) | 📧 bryan.tegomoh@berkeley.edu
    """,
    examples=examples,
    theme=gr.themes.Soft(),
    analytics_enabled=False,
)

if __name__ == "__main__":
    demo.launch()
