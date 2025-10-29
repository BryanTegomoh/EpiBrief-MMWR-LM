"""
EpiBrief-MMWR-LM Fine-Tuning Script for Tinker API

This script fine-tunes Llama 3.1 8B on 11,632 CDC MMWR training pairs
to create a specialized epidemiological reasoning model.

Based on: tinker-cookbook/tinker_cookbook/recipes/sl_loop.py
Adapted for: JSONL instruction-response format
Purpose: World-class epidemiological brief generation

Author: Claude (Anthropic) & Bryan
Date: 2025-10-29
Model: meta-llama/Llama-3.1-8B (Base)
Quality: Professional-grade for medical deployment
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List

import tinker
from tinker_cookbook import checkpoint_utils, model_info, renderers
from tinker_cookbook.supervised.common import compute_mean_nll, datum_from_tokens_weights
from tinker_cookbook.tokenizer_utils import get_tokenizer
from tinker_cookbook.utils import ml_log

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARN)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Training configuration for EpiBrief-MMWR-LM."""

    # API Configuration
    base_url: str | None = None  # Tinker API URL (None = default)

    # Paths
    log_path: str = "../logs/epibrief-training"  # Checkpoints saved here
    train_data_path: str = "../training_data/train.jsonl"
    val_data_path: str = "../training_data/val.jsonl"

    # Model Selection (CRITICAL CHOICE)
    model_name: str = "meta-llama/Llama-3.1-8B"  # Base model (NOT Instruct)
    # Alternative: "Qwen/Qwen3-8B" for comparison

    # Training Hyperparameters
    batch_size: int = 4  # Start small, can increase to 8-16
    learning_rate: float = 1e-4  # Standard for LoRA
    num_epochs: int = 3  # Typically 2-5 epochs for fine-tuning
    max_length: int = 4096  # Max sequence length (your pairs are shorter)

    # LoRA Configuration
    lora_rank: int = 32  # Tinker default, works well

    # Training Control
    train_on_what: renderers.TrainOnWhat = renderers.TrainOnWhat.ALL_ASSISTANT_MESSAGES
    save_every: int = 50  # Save checkpoint every N batches
    log_every: int = 10  # Log metrics every N batches
    sample_every: int = 100  # Generate validation samples every N batches

    # Quality Assurance
    min_quality_score: float = 0.5  # Skip low-quality pairs (optional)
    shuffle_seed: int = 42  # Reproducibility


# ============================================================================
# DATA LOADING
# ============================================================================

class EpiBriefDataset:
    """
    Dataset loader for EpiBrief JSONL training pairs.

    Converts instruction-response pairs into Message format for Tinker.
    """

    def __init__(self, jsonl_path: str, batch_size: int, min_quality: float = 0.0):
        self.jsonl_path = Path(jsonl_path)
        self.batch_size = batch_size
        self.min_quality = min_quality
        self.data = self._load_and_filter()

        logger.info(f"Loaded {len(self.data)} training pairs from {jsonl_path}")
        if min_quality > 0:
            logger.info(f"Filtered to quality >= {min_quality}")

    def _load_and_filter(self) -> List[Dict]:
        """Load JSONL and filter by quality score."""
        data = []
        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                pair = json.loads(line)
                # Optional: filter by quality score
                if pair.get('quality_score', 1.0) >= self.min_quality:
                    data.append(pair)
        return data

    def pair_to_messages(self, pair: Dict) -> List[renderers.Message]:
        """
        Convert instruction-response pair to Message format.

        Format:
        [
            {"role": "user", "content": "<instruction>"},
            {"role": "assistant", "content": "<response>"}
        ]
        """
        return [
            renderers.Message(role="user", content=pair['instruction']),
            renderers.Message(role="assistant", content=pair['response'])
        ]

    def shuffle(self, seed: int = 0):
        """Shuffle dataset for new epoch."""
        import random
        random.seed(seed)
        random.shuffle(self.data)

    def get_batch(self, batch_idx: int) -> List[List[renderers.Message]]:
        """Get batch of conversations."""
        start_idx = batch_idx * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.data))

        batch = []
        for pair in self.data[start_idx:end_idx]:
            messages = self.pair_to_messages(pair)
            batch.append(messages)

        return batch

    def __len__(self) -> int:
        import math
        return math.ceil(len(self.data) / self.batch_size)


# ============================================================================
# TRAINING LOOP
# ============================================================================

def train_epibrief_model(config: Config):
    """
    Main training loop for EpiBrief-MMWR-LM.

    This implements supervised fine-tuning on CDC-quality training pairs
    to teach the model epidemiological reasoning and brief generation.
    """

    print("\n" + "="*80)
    print("   EpiBrief-MMWR-LM Fine-Tuning")
    print("   Model: " + config.model_name)
    print("   Training pairs: " + str(config.train_data_path))
    print("="*80 + "\n")

    # ========================================================================
    # SETUP: Logging, Tokenizer, Renderer
    # ========================================================================

    # Create log directory (checkpoints will be saved here)
    Path(config.log_path).mkdir(parents=True, exist_ok=True)

    # Setup ML logging (WandB optional)
    ml_logger = ml_log.setup_logging(
        log_dir=config.log_path,
        wandb_project=None,  # Set to "epibrief-mmwr-lm" to use WandB
        wandb_name=None,
        config=vars(config),
        do_configure_logging_module=True,
    )

    logger.info(f"Training configuration:")
    for key, value in vars(config).items():
        logger.info(f"  {key}: {value}")

    # Get tokenizer and renderer for the model
    tokenizer = get_tokenizer(config.model_name)
    renderer_name = model_info.get_recommended_renderer_name(config.model_name)
    renderer = renderers.get_renderer(renderer_name, tokenizer)
    logger.info(f"Using renderer: {renderer_name}")

    # ========================================================================
    # LOAD DATA
    # ========================================================================

    logger.info("Loading training data...")
    train_dataset = EpiBriefDataset(
        config.train_data_path,
        config.batch_size,
        config.min_quality_score
    )

    logger.info("Loading validation data...")
    val_dataset = EpiBriefDataset(
        config.val_data_path,
        config.batch_size,
        config.min_quality_score
    )

    n_train_batches = len(train_dataset)
    n_val_batches = len(val_dataset)

    logger.info(f"Train: {len(train_dataset.data)} pairs ({n_train_batches} batches)")
    logger.info(f"Val:   {len(val_dataset.data)} pairs ({n_val_batches} batches)")

    # ========================================================================
    # SETUP TINKER CLIENT
    # ========================================================================

    logger.info("Connecting to Tinker API...")
    service_client = tinker.ServiceClient(base_url=config.base_url)

    # Check for resuming from checkpoint
    resume_info = checkpoint_utils.get_last_checkpoint(config.log_path)
    if resume_info:
        logger.info(f"Resuming from batch {resume_info['batch']}")
        training_client = service_client.create_training_client_from_state(
            resume_info["state_path"]
        )
        start_batch = resume_info["batch"]
        start_epoch = resume_info.get("epoch", 0)
    else:
        logger.info("Creating new LoRA training client...")
        training_client = service_client.create_lora_training_client(
            base_model=config.model_name,
            rank=config.lora_rank
        )
        start_batch = 0
        start_epoch = 0

    logger.info(f"✓ Connected to Tinker")
    logger.info(f"✓ Model: {config.model_name}")
    logger.info(f"✓ LoRA rank: {config.lora_rank}")

    # ========================================================================
    # TRAINING LOOP
    # ========================================================================

    total_batches_processed = 0

    for epoch in range(start_epoch, config.num_epochs):
        logger.info(f"\n{'='*80}")
        logger.info(f"EPOCH {epoch + 1}/{config.num_epochs}")
        logger.info('='*80)

        # Shuffle dataset for this epoch
        train_dataset.shuffle(seed=config.shuffle_seed + epoch)

        epoch_start_time = time.time()
        epoch_loss = 0.0
        epoch_batches = 0

        # Determine starting batch for this epoch
        if epoch == start_epoch and resume_info:
            batch_start = start_batch % n_train_batches
        else:
            batch_start = 0

        for batch_idx in range(batch_start, n_train_batches):
            batch_start_time = time.time()

            # Global step across all epochs
            global_step = epoch * n_train_batches + batch_idx

            # ================================================================
            # SAVE CHECKPOINT
            # ================================================================

            if global_step % config.save_every == 0 and global_step > 0:
                logger.info(f"Saving checkpoint at step {global_step}...")
                checkpoint_utils.save_checkpoint(
                    training_client=training_client,
                    name=f"epoch{epoch + 1}_step{global_step:06d}",
                    log_path=config.log_path,
                    kind="state",
                    loop_state={"batch": batch_idx, "epoch": epoch}
                )

            # ================================================================
            # LEARNING RATE SCHEDULE (Linear decay)
            # ================================================================

            total_steps = config.num_epochs * n_train_batches
            progress = global_step / total_steps
            lr_mult = max(0.1, 1.0 - progress)  # Min LR = 10% of initial
            current_lr = config.learning_rate * lr_mult

            adam_params = tinker.AdamParams(
                learning_rate=current_lr,
                beta1=0.9,
                beta2=0.95,
                eps=1e-8
            )

            # ================================================================
            # GET BATCH AND CONVERT TO DATUMS
            # ================================================================

            batch_conversations = train_dataset.get_batch(batch_idx)

            # Convert each conversation to Datum format
            batch_datums = []
            for conversation in batch_conversations:
                # Use renderer to create tokens and weights (returns tensors)
                tokens, weights = renderer.build_supervised_example(
                    conversation,
                    train_on_what=config.train_on_what
                )
                # Create Datum (pass tensors directly, helper calls .tolist() internally)
                datum = datum_from_tokens_weights(
                    tokens,
                    weights,
                    config.max_length
                )
                batch_datums.append(datum)

            # ================================================================
            # TRAINING STEP
            # ================================================================

            # Forward + Backward pass
            fwd_bwd_future = training_client.forward_backward(
                batch_datums,
                loss_fn="cross_entropy"
            )

            # Optimizer step
            optim_step_future = training_client.optim_step(adam_params)

            # Wait for completion
            fwd_bwd_result = fwd_bwd_future.result()
            _optim_result = optim_step_future.result()

            # ================================================================
            # COMPUTE METRICS
            # ================================================================

            # Extract logprobs and weights
            train_logprobs = [x["logprobs"] for x in fwd_bwd_result.loss_fn_outputs]
            train_weights = [d.loss_fn_inputs["weights"] for d in batch_datums]
            train_nll = compute_mean_nll(train_logprobs, train_weights)

            epoch_loss += train_nll
            epoch_batches += 1

            # ================================================================
            # LOGGING
            # ================================================================

            if batch_idx % config.log_every == 0 or batch_idx == n_train_batches - 1:
                batch_time = time.time() - batch_start_time
                tokens_per_sec = sum(d.model_input.length for d in batch_datums) / batch_time

                metrics = {
                    "epoch": epoch + 1,
                    "batch": batch_idx,
                    "global_step": global_step,
                    "train_nll": train_nll,
                    "learning_rate": current_lr,
                    "lr_mult": lr_mult,
                    "progress": progress,
                    "num_sequences": len(batch_datums),
                    "num_tokens": sum(d.model_input.length for d in batch_datums),
                    "tokens_per_sec": tokens_per_sec,
                    "batch_time": batch_time,
                }

                ml_logger.log_metrics(metrics=metrics, step=global_step)

                logger.info(
                    f"Epoch {epoch+1}/{config.num_epochs} | "
                    f"Batch {batch_idx}/{n_train_batches} | "
                    f"Loss: {train_nll:.4f} | "
                    f"LR: {current_lr:.2e} | "
                    f"Tokens/s: {tokens_per_sec:.1f}"
                )

            # ================================================================
            # VALIDATION SAMPLING (Optional)
            # ================================================================

            if batch_idx % config.sample_every == 0 and batch_idx > 0:
                logger.info("\n--- Validation Sample ---")

                # Get a validation example
                val_batch = val_dataset.get_batch(0)
                val_conversation = val_batch[0]

                # Extract instruction (TypedDict is runtime dict, use subscript)
                instruction = val_conversation[0]["content"][:100]
                expected_response = val_conversation[1]["content"][:200]

                # Generate from model
                prompt = renderer.build_generation_prompt(
                    [val_conversation[0]],  # Just the user message
                    role="assistant"
                )

                # Sample from training client
                # Note: This requires sampling capability from training client
                # May need to use save_weights_and_get_sampling_client() for actual sampling
                logger.info(f"Instruction: {instruction}...")
                logger.info(f"Expected: {expected_response}...")
                logger.info("(Actual sampling deferred to evaluation phase)")
                logger.info("-" * 40 + "\n")

            total_batches_processed += 1

        # ====================================================================
        # END OF EPOCH
        # ====================================================================

        epoch_time = time.time() - epoch_start_time
        avg_epoch_loss = epoch_loss / epoch_batches

        logger.info(f"\n{'='*80}")
        logger.info(f"Epoch {epoch + 1} Complete")
        logger.info(f"  Average Loss: {avg_epoch_loss:.4f}")
        logger.info(f"  Time: {epoch_time:.1f}s")
        logger.info(f"  Batches: {epoch_batches}")
        logger.info('='*80 + "\n")

        # Save end-of-epoch checkpoint
        checkpoint_utils.save_checkpoint(
            training_client=training_client,
            name=f"epoch{epoch + 1}_final",
            log_path=config.log_path,
            kind="both",  # Save both state and weights
            loop_state={"batch": n_train_batches, "epoch": epoch + 1}
        )

    # ========================================================================
    # TRAINING COMPLETE
    # ========================================================================

    logger.info("\n" + "="*80)
    logger.info("Training Complete!")
    logger.info("="*80)

    # Save final model
    logger.info("Saving final checkpoint...")
    checkpoint_utils.save_checkpoint(
        training_client=training_client,
        name="final",
        log_path=config.log_path,
        kind="both",
        loop_state={"batch": n_train_batches, "epoch": config.num_epochs}
    )

    # Get sampling client for inference
    logger.info("Creating sampling client...")
    sampling_client = training_client.save_weights_and_get_sampling_client(
        name="epibrief-mmwr-lm-v1"
    )

    logger.info(f"✓ Model saved to Tinker path: {sampling_client.model_path}")
    logger.info(f"✓ Local checkpoint directory: {Path(config.log_path).absolute()}")
    logger.info(f"✓ Total batches processed: {total_batches_processed}")
    logger.info(f"✓ Total training pairs seen: {total_batches_processed * config.batch_size}")

    # Download weights (with clearer instructions)
    logger.info("\n" + "="*80)
    logger.info("TO DOWNLOAD LORA WEIGHTS FOR LOCAL INFERENCE:")
    logger.info("="*80)
    logger.info(f"rest_client = service_client.create_rest_client()")
    logger.info(f"future = rest_client.download_checkpoint_archive_from_tinker_path('{sampling_client.model_path}')")
    logger.info(f"with open('epibrief-lora-weights.tar.gz', 'wb') as f:")
    logger.info(f"    f.write(future.result())")
    logger.info(f"\nThen extract and use with your base model ({config.model_name})")

    ml_logger.close()

    print("\n" + "="*80)
    print("✓ Training successful!")
    print("✓ Model ready for evaluation")
    print("✓ Next: Evaluate on test MMWR articles")
    print("="*80 + "\n")

    return sampling_client


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point with argument parsing."""

    # Check for API key
    if "TINKER_API_KEY" not in os.environ:
        raise ValueError(
            "TINKER_API_KEY environment variable not set!\n"
            "Get your key from: https://tinker-console.thinkingmachines.ai\n"
            "Then set: $env:TINKER_API_KEY = 'your-key-here'"
        )

    # Initialize config
    config = Config()

    # Check data files exist
    if not Path(config.train_data_path).exists():
        raise FileNotFoundError(
            f"Training data not found: {config.train_data_path}\n"
            f"Run: python 4_split_dataset.py first!"
        )

    if not Path(config.val_data_path).exists():
        raise FileNotFoundError(
            f"Validation data not found: {config.val_data_path}\n"
            f"Run: python 4_split_dataset.py first!"
        )

    logger.info("="*80)
    logger.info("EpiBrief-MMWR-LM Training Script")
    logger.info("Professional-grade epidemiological reasoning model")
    logger.info("="*80)

    # Run training
    try:
        sampling_client = train_epibrief_model(config)
        logger.info("\n✓ Success! Model ready for deployment.")
        return sampling_client

    except Exception as e:
        logger.error(f"\n✗ Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
