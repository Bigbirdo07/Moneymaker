# Genuine MMRM-0.1 QLoRA Training Experiment Report

## 1. Experiment Overview
- **Experiment Identifier**: `EXP_MMRM_REAL_V2`
- **Candidate Model**: `MMRM-0.1-REAL`
- **Base Architecture**: `Qwen2.5-14B-Instruct`
- **Training Dataset**: `DS_MM_LLM_V2` (`train.jsonl`, 416 examples; `val.jsonl`, 52 examples)
- **Dataset Hash (SHA-256)**: `66256e48bc5c26a156f8b041f34b5b12a3efcd4b2760717d6d92fc5c373e84bb`
- **Slurm Script**: `jobs/llm_finetune.slurm`
- **Target Partition**: `uri-gpu` (NVIDIA A100-SXM4-80GB)

---

## 2. Hyperparameter Configuration

| Parameter | Value | Justification |
|---|---|---|
| Quantization | 4-bit NF4 (Double Quant) | Fit 14.7B model + adapters within VRAM with bfloat16 compute |
| LoRA Rank ($r$) | 16 | Sufficient capacity for domain instruction tuning |
| LoRA Alpha ($\alpha$) | 32 | Standard $2 \times r$ scaling factor |
| LoRA Dropout | 0.05 | Regularization against small-sample overfitting |
| Target Modules | `q, k, v, o, gate, up, down` | All attention & MLP projection layers |
| Learning Rate | $2.0 \times 10^{-4}$ | Paged AdamW 8-bit optimizer with cosine decay |
| Batch Size / Accumulation | $2 \times 8 = 16$ | Effective batch size of 16 sequences |
| Training Epochs | 3 | Early stopping evaluated on validation split |
| Max Sequence Length | 1,024 tokens | Covers multi-turn tool calling and context payloads |

---

## 3. Training Script Diagnostics
The genuine entrypoint [`src/research/runners/run_qlora_finetune.py`](file:///Users/albertopaz/Moneymaker/src/research/runners/run_qlora_finetune.py) executes:
1. Real tokenization and formatting of `DS_MM_LLM_V2`.
2. Hardware telemetry collection (`environment.json`).
3. Loss curve trajectory logging.
4. Serialized saving of genuine PEFT checkpoints (`adapter_config.json`, `adapter_model.safetensors`).
