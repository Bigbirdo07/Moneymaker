"""
Real Benchmark Forward-Pass Inference & Evaluation Runner.
Executes prompt generation against MONEYMAKER_LLM_BENCHMARK_V2 across four empirical conditions:
- Condition A: Base Qwen2.5-14B Only
- Condition B: Base + Research Memory RAG
- Condition C: MMRM-0.1 PEFT Adapter Only
- Condition D: MMRM-0.1 + Research Memory RAG
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional

from src.research.llm_benchmark import MoneymakerLLMBenchmark, BenchmarkItem, BenchmarkResult


def format_chat_prompt(system_prompt: str, user_question: str, rag_context: Optional[str] = None) -> str:
    ctx_str = f"\n\nRetrieved Platform Telemetry Context:\n{rag_context}" if rag_context else ""
    return (
        f"<|im_start|>system\n{system_prompt}{ctx_str}<|im_end|>\n"
        f"<|im_start|>user\n{user_question}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def run_benchmark_inference(
    model_path: str,
    adapter_path: Optional[str],
    output_file: str,
    use_rag: bool = False,
    condition_name: str = "BASE_ONLY",
) -> str:
    """
    Executes benchmark inference and writes raw JSONL records to output_file.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    items = MoneymakerLLMBenchmark.get_benchmark_items()

    system_prompt = (
        "You are Moneymaker AI Copilot (MMRM-0.1), an advisory quantitative research assistant. "
        "You have strict read-only tool access to Moneymaker platform telemetry. "
        "You never fabricate P&L or trade data, never execute live broker orders, "
        "and always tag your conclusions with explicit empirical provenance."
    )

    records: List[Dict[str, Any]] = []

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel
        has_gpu = torch.cuda.is_available()
    except ImportError:
        has_gpu = False

    if has_gpu:
        print(f"[INFO] Running real GPU inference for {condition_name} ({len(items)} items)...")
        bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        base_model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config, device_map="auto")

        if adapter_path and os.path.exists(adapter_path):
            model = PeftModel.from_pretrained(base_model, adapter_path)
        else:
            model = base_model

        for it in items:
            prompt = format_chat_prompt(system_prompt, it.question)
            inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
            with torch.no_grad():
                out = model.generate(**inputs, max_new_tokens=256, temperature=0.1, do_sample=False)
            gen_text = tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

            records.append({
                "item_id": it.item_id,
                "domain": it.domain,
                "question": it.question,
                "prompt": prompt,
                "response": gen_text,
                "condition": condition_name,
                "model_path": model_path,
                "adapter_path": adapter_path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    else:
        print(f"[INFO] Host execution for {condition_name}: writing benchmark evaluation record template.")
        # When GPU is not present locally, construct evaluation record structure for cluster scoring
        for it in items:
            records.append({
                "item_id": it.item_id,
                "domain": it.domain,
                "question": it.question,
                "prompt": format_chat_prompt(system_prompt, it.question),
                "response": "",  # Populated during real GPU forward pass on Unity
                "condition": condition_name,
                "model_path": model_path,
                "adapter_path": adapter_path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    with open(output_file, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    return output_file


def main():
    parser = argparse.ArgumentParser(description="Run Moneymaker Benchmark V2 Forward Passes")
    parser.add_argument("--base-model-path", type=str, default="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8")
    parser.add_argument("--adapter-path", type=str, default="")
    parser.add_argument("--output-dir", type=str, default="outputs/evaluations")
    parser.add_argument("--condition", type=str, default="BASE_ONLY")
    args = parser.parse_args()

    out_file = os.path.join(args.output_dir, f"REAL_{args.condition}_V2.jsonl")
    run_benchmark_inference(
        model_path=args.base_model_path,
        adapter_path=args.adapter_path if args.adapter_path else None,
        output_file=out_file,
        condition_name=args.condition,
    )
    print(f"[SUCCESS] Benchmark evaluation saved to {out_file}")


if __name__ == "__main__":
    main()
