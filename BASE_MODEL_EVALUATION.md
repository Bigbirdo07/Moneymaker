# Open-Source LLM Base Model Evaluation & Selection

## 1. Candidate Comparison Matrix

To construct the **Moneymaker Research Model** (`MMRM-0.1`), several leading open-source instruction-tuned foundation models were evaluated across quantitative reasoning capabilities, structured tool calling, licensing, context length, and Unity HPC hardware fit.

| Model Candidate | Parameters | License | Tool Calling Support | Context Length | Unity GPU Memory Fit (4-bit QLoRA) | Pre-Cached on Unity Cluster |
|---|---|---|---|---|---|---|
| **Qwen 2.5 14B Instruct** | **14.7B** | **Apache 2.0 (Permissive)** | **Exceptional** | **128k tokens** | **~11 GB VRAM (Fits 1x GPU cleanly)** | **YES (52GB Cache Available)** |
| **Llama 3.1 8B Instruct** | 8.0B | Llama 3.1 Community | Good | 128k tokens | ~6 GB VRAM | No |
| **Llama 3.1 70B Instruct** | 70.6B | Llama 3.1 Community | Exceptional | 128k tokens | ~48 GB VRAM (Requires multi-GPU) | No |
| **Mistral NeMo 12B** | 12.2B | Apache 2.0 | Moderate | 128k tokens | ~9 GB VRAM | No |
| **DeepSeek R1 Distill Qwen 14B** | 14.7B | MIT | Moderate (Specialized CoT) | 64k tokens | ~11 GB VRAM | No |

---

## 2. Selection Rationale: Qwen 2.5 14B Instruct

**Selected Foundation Model**: `Qwen/Qwen2.5-14B-Instruct`

### Key Deciding Factors:
1. **Direct Availability on Unity Cluster**:
   - Model weights (52GB snapshot) already reside in `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8/`.
   - Accessible with **zero network download overhead** and **zero duplicate disk usage**.
2. **Permissive Apache 2.0 License**:
   - Allows commercial and proprietary fine-tuning with zero telemetry or restrictive deployment covenants.
3. **Leading Quantitative & Tool-Calling Benchmarks**:
   - Outperforms 8B and 13B peers on math/code/reasoning benchmarks (GSM8K, MATH, HumanEval).
   - Superior structured JSON formatting adherence required by the 28-tool Moneymaker Copilot interface.
4. **Hardware Efficiency**:
   - 4-bit NF4 quantized base consumes only ~11GB VRAM, enabling high batch size training with LoRA rank 16 on a single Unity GPU (`uri-gpu` partition).
