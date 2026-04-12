#!/usr/bin/env python3
"""
train_lora.py — LoRA fine-tuning of OPT-350M-Erebus on LEX legal framework data.

Applies Parameter-Efficient Fine-Tuning (PEFT) with LoRA adapters targeting
the attention projections (q_proj, v_proj), adding ~1.6M trainable parameters
on top of the frozen 331M base model.

Prerequisites:
    pip install transformers peft datasets accelerate bitsandbytes

Usage:
    # Prepare data first
    python prepare_legal_data.py --all --output-dir ./training_data

    # Train with LoRA
    python train_lora.py \
        --train-file ./training_data/train_instruction.jsonl \
        --output-dir ./e350-lex-lora \
        --epochs 3 \
        --batch-size 4 \
        --learning-rate 2e-4 \
        --lora-rank 16 \
        --lora-alpha 32

    # Merge LoRA weights into base model (optional)
    python train_lora.py --merge \
        --lora-dir ./e350-lex-lora \
        --output-dir ./e350-lex-merged

    # Convert to GGUF for KoboldCpp (optional)
    python train_lora.py --convert-gguf \
        --merged-dir ./e350-lex-merged \
        --output-dir ./e350-lex-gguf
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def check_dependencies():
    """Check that required packages are installed."""
    missing = []
    for pkg in ["transformers", "peft", "datasets", "accelerate"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)


def load_training_data(train_file: str, eval_split: float = 0.1):
    """Load and split training data from JSONL file."""
    from datasets import Dataset

    samples = []
    with open(train_file) as f:
        for line in f:
            sample = json.loads(line.strip())
            # Format as text for causal LM training
            text = (
                f"[Genre: {sample.get('genre_tag', 'legal')}]\n"
                f"[Task: {sample.get('task', 'analysis')}]\n"
                f"{sample['instruction']}\n"
                f"---\n"
                f"{sample['response']}<|endoftext|>"
            )
            samples.append({"text": text})

    dataset = Dataset.from_list(samples)
    split = dataset.train_test_split(test_size=eval_split, seed=42)
    print(f"Training samples: {len(split['train'])}, Eval samples: {len(split['test'])}")
    return split


def setup_model_and_lora(
    model_name: str = "KoboldAI/OPT-350M-Erebus",
    lora_rank: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    target_modules: list[str] = None,
):
    """Load base model and apply LoRA configuration."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model, TaskType

    if target_modules is None:
        target_modules = ["q_proj", "v_proj"]

    print(f"Loading base model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
    )

    # Ensure pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id

    # LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
        bias="none",
    )

    model = get_peft_model(model, lora_config)

    # Report parameter counts
    trainable, total = model.get_nb_trainable_parameters()
    print(f"Total parameters: {total:,}")
    print(f"Trainable parameters: {trainable:,} ({100 * trainable / total:.2f}%)")
    print(f"LoRA rank: {lora_rank}, alpha: {lora_alpha}")
    print(f"Target modules: {target_modules}")

    return model, tokenizer


def tokenize_dataset(dataset, tokenizer, max_length: int = 512):
    """Tokenize dataset for causal language modeling."""

    def tokenize_fn(examples):
        tokens = tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    tokenized = dataset.map(tokenize_fn, batched=True, remove_columns=["text"])
    return tokenized


def train(
    train_file: str,
    output_dir: str,
    model_name: str = "KoboldAI/OPT-350M-Erebus",
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4,
    max_length: int = 512,
    lora_rank: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    target_modules: list[str] = None,
    warmup_steps: int = 50,
    logging_steps: int = 10,
    save_steps: int = 100,
    eval_steps: int = 50,
):
    """Run LoRA fine-tuning."""
    from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

    # Load data
    print("\n[1/4] Loading training data...")
    dataset_split = load_training_data(train_file)

    # Setup model
    print("\n[2/4] Setting up model with LoRA...")
    model, tokenizer = setup_model_and_lora(
        model_name=model_name,
        lora_rank=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
    )

    # Tokenize
    print("\n[3/4] Tokenizing dataset...")
    train_dataset = tokenize_dataset(dataset_split["train"], tokenizer, max_length)
    eval_dataset = tokenize_dataset(dataset_split["test"], tokenizer, max_length)

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Causal LM, not masked LM
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_steps=warmup_steps,
        logging_steps=logging_steps,
        save_steps=save_steps,
        eval_steps=eval_steps,
        eval_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,
        gradient_accumulation_steps=4,
        report_to="none",
        save_total_limit=3,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    # Train
    print("\n[4/4] Training...")
    trainer.train()

    # Save
    print(f"\nSaving LoRA adapter to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Save training metadata
    meta = {
        "base_model": model_name,
        "lora_rank": lora_rank,
        "lora_alpha": lora_alpha,
        "lora_dropout": lora_dropout,
        "target_modules": target_modules or ["q_proj", "v_proj"],
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "max_length": max_length,
        "train_samples": len(dataset_split["train"]),
        "eval_samples": len(dataset_split["test"]),
        "composition": "e350-lex = skill-infinity(e350-mlp ⊗ nn ⊗ (lex ⊕ sleuth ⊕ holmes ⊕ foreknowledge))",
    }
    with open(os.path.join(output_dir, "training_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("Training complete!")
    return trainer


def merge_lora(lora_dir: str, output_dir: str, model_name: str = "KoboldAI/OPT-350M-Erebus"):
    """Merge LoRA weights into base model."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print(f"Loading base model: {model_name}")
    base_model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print(f"Loading LoRA adapter: {lora_dir}")
    model = PeftModel.from_pretrained(base_model, lora_dir)

    print("Merging weights...")
    merged = model.merge_and_unload()

    print(f"Saving merged model to {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    merged.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Merge complete!")


def convert_gguf(merged_dir: str, output_dir: str):
    """Convert merged model to GGUF format for KoboldCpp."""
    import subprocess

    print("Converting to GGUF format...")
    print("This requires llama.cpp's convert script.")

    # Check for convert script
    convert_script = Path.home() / "llama.cpp" / "convert_hf_to_gguf.py"
    if not convert_script.exists():
        print(f"llama.cpp not found. Clone it first:")
        print(f"  git clone https://github.com/ggerganov/llama.cpp ~/llama.cpp")
        print(f"  pip install -r ~/llama.cpp/requirements.txt")
        print(f"\nThen run:")
        print(f"  python {convert_script} {merged_dir} --outfile {output_dir}/e350-lex.gguf --outtype f16")
        print(f"  ~/llama.cpp/build/bin/llama-quantize {output_dir}/e350-lex.gguf {output_dir}/e350-lex-Q4_K_M.gguf Q4_K_M")
        return

    os.makedirs(output_dir, exist_ok=True)
    gguf_path = os.path.join(output_dir, "e350-lex.gguf")

    subprocess.run([
        sys.executable, str(convert_script),
        merged_dir,
        "--outfile", gguf_path,
        "--outtype", "f16",
    ], check=True)

    print(f"GGUF saved to {gguf_path}")
    print(f"Quantize with: llama-quantize {gguf_path} {output_dir}/e350-lex-Q4_K_M.gguf Q4_K_M")


def main():
    parser = argparse.ArgumentParser(description="LoRA fine-tuning of Erebus 350M on LEX legal data")

    # Mode
    parser.add_argument("--merge", action="store_true", help="Merge LoRA into base model")
    parser.add_argument("--convert-gguf", action="store_true", help="Convert merged model to GGUF")

    # Training args
    parser.add_argument("--train-file", type=str, help="Path to training JSONL file")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    parser.add_argument("--model-name", type=str, default="KoboldAI/OPT-350M-Erebus")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--target-modules", nargs="+", default=["q_proj", "v_proj"])

    # Merge args
    parser.add_argument("--lora-dir", type=str, help="Path to LoRA adapter directory")
    parser.add_argument("--merged-dir", type=str, help="Path to merged model directory")

    args = parser.parse_args()

    if args.merge:
        check_dependencies()
        merge_lora(args.lora_dir or args.output_dir, args.output_dir, args.model_name)
    elif args.convert_gguf:
        convert_gguf(args.merged_dir or args.output_dir, args.output_dir)
    else:
        check_dependencies()
        if not args.train_file:
            parser.error("--train-file is required for training")
        train(
            train_file=args.train_file,
            output_dir=args.output_dir,
            model_name=args.model_name,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            max_length=args.max_length,
            lora_rank=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            target_modules=args.target_modules,
        )


if __name__ == "__main__":
    main()
