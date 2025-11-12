"""
EpiBrief-MMWR-LM: CDC-Style Epidemiological Reasoning AI (IMPROVED VERSION)
Hugging Face Space Demo with Anti-Measles-Bias Fixes

Author: Bryan Tegomoh, MD, MPH
Model: Fine-tuned Llama 3.1 8B on 11,632 CDC MMWR training pairs

IMPROVEMENTS:
1. Better sampling parameters (temperature, top_p, repetition_penalty)
2. Disease-specific prompt engineering
3. Multi-candidate generation with filtering
4. Vocabulary constraints to suppress measles bias
5. Output validation and re-ranking
"""

import gradio as gr
import os
import re
from collections import Counter

# Check if running on Hugging Face Spaces
IS_SPACES = os.environ.get("SPACE_ID") is not None

# Set Tinker API key from HuggingFace secret (if available)
if IS_SPACES and os.environ.get("TINKER_API_KEY"):
    os.environ["TINKER_API_KEY"] = os.environ.get("TINKER_API_KEY")

# Try to import tinker (works if API key is set locally or on HF Spaces)
HAS_TINKER = False
try:
    import tinker
    from tinker import types
    from tinker_cookbook import renderers, model_info
    from tinker_cookbook.tokenizer_utils import get_tokenizer
    HAS_TINKER = True
except ImportError:
    pass

# Disease keywords for intelligent prompting
DISEASE_KEYWORDS = {
    "covid": ["covid", "coronavirus", "sars-cov-2", "pandemic"],
    "influenza": ["influenza", "flu", "h1n1", "h3n2"],
    "measles": ["measles", "mmr", "rubeola"],
    "tuberculosis": ["tuberculosis", "tb", "mycobacterium"],
    "hiv": ["hiv", "aids", "human immunodeficiency"],
    "dengue": ["dengue", "aedes", "flavivirus"],
    "malaria": ["malaria", "plasmodium", "anopheles"],
    "ebola": ["ebola", "hemorrhagic fever", "filovirus"],
    "monkeypox": ["monkeypox", "mpox", "orthopoxvirus"],
    "hepatitis": ["hepatitis", "hbv", "hcv"],
}

def detect_disease(text):
    """Detect which disease is mentioned in the query"""
    text_lower = text.lower()

    for disease, keywords in DISEASE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return disease

    return "unknown"

def build_disease_specific_prompt(user_input, task_type, detected_disease):
    """Build prompt that explicitly frames the disease context"""

    disease_context = {
        "covid": "COVID-19 pandemic",
        "influenza": "seasonal influenza",
        "measles": "measles outbreak",
        "tuberculosis": "tuberculosis transmission",
        "hiv": "HIV/AIDS epidemic",
        "dengue": "dengue fever outbreak",
        "malaria": "malaria surveillance",
        "ebola": "Ebola virus disease",
        "monkeypox": "monkeypox outbreak",
        "hepatitis": "viral hepatitis",
        "unknown": "infectious disease outbreak"
    }

    context = disease_context.get(detected_disease, "infectious disease outbreak")

    task_prompts = {
        "Executive Summary": f"""You are a CDC epidemiologist specializing in {context}.

Context: {user_input}

Task: Generate a CDC-style executive summary with:
- What is already known about this topic?
- What is added by this report?
- What are the implications for public health practice?

Focus specifically on {detected_disease if detected_disease != 'unknown' else 'this disease'}.

Executive Summary:""",

        "Data Interpretation": f"""You are a CDC epidemiologist analyzing {context} data.

Data: {user_input}

Task: Interpret the epidemiological findings, focusing on:
- Key patterns and trends
- Demographic and geographic distributions
- Public health significance

Analysis:""",

        "Public Health Implications": f"""You are a CDC epidemiologist assessing {context} response strategies.

Findings: {user_input}

Task: Describe public health implications and recommendations specific to {detected_disease if detected_disease != 'unknown' else 'this outbreak'}.

Implications:""",

        "Outbreak Analysis": f"""You are a CDC epidemiologist investigating a {context} scenario.

Outbreak scenario: {user_input}

Task: Provide epidemiological analysis including transmission patterns, risk factors, and control measures.

Analysis:"""
    }

    return task_prompts.get(task_type, f"Analyze this {context} situation:\n\n{user_input}\n\nAnalysis:")

def calculate_output_score(output_text, user_input, detected_disease):
    """Score output for relevance and quality"""
    score = 0.0

    # Check if detected disease appears in output
    if detected_disease != "unknown":
        disease_keywords = DISEASE_KEYWORDS.get(detected_disease, [])
        if any(kw in output_text.lower() for kw in disease_keywords):
            score += 3.0
        else:
            score -= 2.0  # Penalize if disease not mentioned

    # Penalize measles mentions when not relevant
    if detected_disease != "measles" and "measles" in output_text.lower():
        score -= 5.0

    # Check output diversity (vocabulary richness)
    words = output_text.lower().split()
    unique_ratio = len(set(words)) / max(len(words), 1)
    score += unique_ratio * 2.0

    # Check if output is too short
    if len(output_text) < 100:
        score -= 1.0

    # Check for CDC-style language
    cdc_phrases = ["public health", "surveillance", "transmission", "outbreak",
                   "epidemiological", "vaccination", "prevention", "control measures"]
    cdc_score = sum(1 for phrase in cdc_phrases if phrase in output_text.lower())
    score += cdc_score * 0.5

    return score

if HAS_TINKER:

    TRAINING_RUN_ID = "dee4e48d-4e45-42d9-9371-a997dac170fd"
    CHECKPOINT_PATH = f"tinker://{TRAINING_RUN_ID}/sampler_weights/epoch3_final"
    MODEL_NAME = "meta-llama/Llama-3.1-8B"

    @gr.cache(cache_examples=False)
    def load_model():
        sc = tinker.ServiceClient()
        tokenizer = get_tokenizer(MODEL_NAME)
        renderer_name = model_info.get_recommended_renderer_name(MODEL_NAME)
        renderer = renderers.get_renderer(renderer_name, tokenizer)
        sampling_client = sc.create_sampling_client(CHECKPOINT_PATH)
        return tokenizer, renderer, sampling_client

    tokenizer, renderer, sampling_client = load_model()

    def generate_epi_summary(user_input, task_type, max_tokens, temperature):
        """Generate epidemiological analysis with improved anti-bias techniques"""

        # FIX #2: Detect disease and build better prompt
        detected_disease = detect_disease(user_input)
        prompt_text = build_disease_specific_prompt(user_input, task_type, detected_disease)

        conversation = [renderers.Message(role="user", content=prompt_text)]
        tokens, _ = renderer.build_supervised_example(
            conversation,
            renderers.TrainOnWhat.ALL_ASSISTANT_MESSAGES
        )

        prompt = types.ModelInput.from_ints(tokens.tolist())

        # FIX #1: Better sampling parameters
        sampling_params = types.SamplingParams(
            max_tokens=int(max_tokens),
            temperature=float(temperature) + 0.15,  # Boost temperature slightly
            top_p=0.92,                              # Nucleus sampling
            top_k=50,                                # Limit vocabulary
            repetition_penalty=1.15,                 # Reduce repetition
            stop=[tokenizer.eos_token]
        )

        try:
            # FIX #3: Generate multiple candidates
            num_candidates = 3  # Generate 3 outputs
            candidates = []

            for _ in range(num_candidates):
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

                # Clean up prompt from output
                if prompt_text in generated_text:
                    generated_text = generated_text.replace(prompt_text, "").strip()

                candidates.append(generated_text)

            # FIX #3 & #5: Score and rank candidates
            scored_candidates = [
                (output, calculate_output_score(output, user_input, detected_disease))
                for output in candidates
            ]

            # Return best candidate
            best_output = max(scored_candidates, key=lambda x: x[1])[0]

            # Add metadata footer
            footer = f"\n\n---\n*Disease context: {detected_disease} | Candidates evaluated: {num_candidates}*"

            return best_output + footer

        except Exception as e:
            return f"Error: {str(e)}\n\nPlease try again or contact bryan.tegomoh@berkeley.edu"

else:
    # Demo mode when Tinker isn't available
    def generate_epi_summary(user_input, task_type, max_tokens, temperature):
        detected_disease = detect_disease(user_input)

        demo_outputs = {
            "covid": """COVID-19 surveillance data indicate ongoing community transmission with fluctuating case rates. Vaccination remains the most effective prevention strategy. Public health officials should focus on maintaining high vaccination coverage, monitoring variant emergence, and strengthening healthcare system capacity. Targeted outreach to undervaccinated communities is essential.""",

            "influenza": """Seasonal influenza activity shows typical patterns with increased cases during winter months. Vaccination coverage remains suboptimal in high-risk groups. Public health priorities include promoting annual flu vaccination, enhancing surveillance systems, and preparing healthcare facilities for surge capacity during peak season.""",

            "measles": """Measles is a highly contagious vaccine-preventable viral disease. Increasing U.S. measles cases have been driven by unvaccinated persons exposed while traveling internationally. Health officials should coordinate response activities to prevent spread, assess vaccination coverage, and ensure MMR vaccination for all eligible children and adults.""",

            "tuberculosis": """Tuberculosis surveillance reveals persistent transmission in high-risk populations. Contact tracing and treatment completion remain critical control measures. Public health strategies should emphasize early detection, appropriate treatment regimens, and addressing social determinants that facilitate TB transmission.""",

            "unknown": """Epidemiological analysis reveals patterns consistent with infectious disease transmission. Public health response should include enhanced surveillance, case investigation, contact tracing, and implementation of evidence-based control measures. Community engagement and clear risk communication are essential."""
        }

        output = demo_outputs.get(detected_disease, demo_outputs["unknown"])
        return f"""**DEMO MODE** (Model not loaded - configure Tinker API to enable)

*Detected disease context: {detected_disease}*

Example output for this disease:

{output}

To use the actual fine-tuned model, run this Space with Tinker API access."""

# Gradio interface
with gr.Blocks(title="EpiBrief-MMWR-LM: AI Epidemiologist") as demo:
    gr.Markdown("""
    # 🦠 EpiBrief-MMWR-LM: AI Epidemiologist

    **Specialized AI trained on 11,632 CDC MMWR training pairs (2016-2025)**

    *Now with improved disease-specific reasoning and reduced measles bias!*

    👨‍⚕️ Developed by: **Bryan Tegomoh, MD, MPH** |
    🔬 Model: Fine-tuned Llama 3.1 8B |
    📊 Training: 85% quantitative focus
    """)

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(
                label="📝 Input Data or Query",
                placeholder="Example: During January 2024, 156 COVID-19 cases were reported in nursing homes across 5 states. Median age 78 years, 64% hospitalized...",
                lines=8
            )

            task_type = gr.Dropdown(
                label="📋 Task Type",
                choices=[
                    "Executive Summary",
                    "Data Interpretation",
                    "Public Health Implications",
                    "Outbreak Analysis"
                ],
                value="Executive Summary"
            )

            with gr.Row():
                max_tokens = gr.Slider(
                    label="📏 Max Length",
                    minimum=100,
                    maximum=600,
                    value=400,
                    step=50
                )

                temperature = gr.Slider(
                    label="🌡️ Temperature",
                    minimum=0.5,
                    maximum=1.2,
                    value=0.7,
                    step=0.1
                )

            submit_btn = gr.Button("🚀 Generate Analysis", variant="primary")

        with gr.Column():
            output = gr.Textbox(
                label="🦠 Generated Analysis",
                lines=15
            )

    gr.Markdown("""
    ### 💡 Tips for Best Results

    - **Be specific**: Mention the disease name (COVID-19, influenza, TB, etc.)
    - **Include data**: Add numbers, dates, demographics for data interpretation tasks
    - **Try different temperatures**: Higher = more creative, Lower = more focused
    - **Evaluate outputs**: This is a research tool - always verify with experts!

    ### 🔧 Recent Improvements

    1. ✅ Better sampling parameters (reduced repetition)
    2. ✅ Disease-specific prompt engineering
    3. ✅ Multi-candidate generation with quality scoring
    4. ✅ Intelligent output ranking and filtering
    5. ✅ Measles bias suppression for non-measles queries

    ### 📚 Resources

    - **Model Weights**: [HuggingFace Hub](https://huggingface.co/BryanTegomoh/EpiBrief-MMWR-LM)
    - **Training Data**: [Dataset](https://huggingface.co/datasets/BryanTegomoh/epibrief-mmwr-training-data)
    - **Source Code**: [GitHub](https://github.com/BryanTegomoh/EpiBrief-MMWR-LM)
    - **Contact**: bryan.tegomoh@berkeley.edu
    """)

    # Examples
    gr.Examples(
        examples=[
            ["During March 2024, 245 COVID-19 cases were reported in long-term care facilities. Among residents, median age was 82 years, 68% were fully vaccinated, and 42% required hospitalization. What are the key findings?", "Data Interpretation", 400, 0.7],
            ["Explain the public health implications of increasing influenza hospitalizations among children under 5 years old this season.", "Public Health Implications", 300, 0.8],
            ["A tuberculosis outbreak was identified in a homeless shelter with 8 confirmed cases over 3 months. Index case had multidrug-resistant TB. Analyze this outbreak.", "Outbreak Analysis", 400, 0.7],
            ["Generate an executive summary for a dengue fever outbreak in Puerto Rico with 1,200 suspected cases and 15% hospitalization rate.", "Executive Summary", 350, 0.75],
        ],
        inputs=[user_input, task_type, max_tokens, temperature],
    )

    submit_btn.click(
        fn=generate_epi_summary,
        inputs=[user_input, task_type, max_tokens, temperature],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()
