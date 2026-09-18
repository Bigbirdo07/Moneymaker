# MMRM-0.2 QLoRA Training Experiment Report

**Status**: SUBMITTED & QUEUED ON UNITY HPC  
**Experiment ID**: `EXP_MMRM_0_2_REAL`  
**Slurm Batch Job ID**: `64519876`  
**Partition**: `uri-gpu` (1x NVIDIA A100/L40S, 8 CPUs, 64GB RAM)  
**Host / User**: `login7.unity.rc.umass.edu` / `alberto_paz_uri_edu`  
**Slurm Submission Record**: [`artifacts/provenance/mmrm_v3_real/training_submission_64519876.txt`](file:///Users/albertopaz/Moneymaker/artifacts/provenance/mmrm_v3_real/training_submission_64519876.txt)  
**Controller Detail**: [`artifacts/provenance/mmrm_v3_real/scontrol_64519876.txt`](file:///Users/albertopaz/Moneymaker/artifacts/provenance/mmrm_v3_real/scontrol_64519876.txt)  

---

## 1. Preregistered Training Hyperparameters

* **Base Model**: `Qwen/Qwen2.5-14B-Instruct` (14.7B parameters)
* **Base Model Path**: `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`
* **Quantization**: 4-bit NF4 (`load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`, `bnb_4bit_use_double_quant=True`, `torch_dtype=bfloat16`)
* **PEFT / LoRA Architecture**:
  * LoRA Rank ($r$): 16
  * LoRA Alpha ($\alpha$): 32
  * LoRA Dropout: 0.05
  * Target Modules: `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
  * Trainable Parameters: **68,812,800** (0.4637%)
* **Optimizer**: `paged_adamw_8bit`
* **Learning Rate**: $1.5 \times 10^{-4}$ (with linear decay to prevent rapid overfitting)
* **Batch Size**: 2 per device (gradient accumulation: 8, effective batch size: 16)
* **Epochs**: 3 (270 optimization steps across 1,440 training examples)
* **Training Dataset**: `data/moneymaker_llm/v3/train.jsonl` (SHA-256: `baa1182e9b866b006cbfcac8467b5c009e95ff456c2b73adee9731ef2639c676`)
* **Validation Dataset**: `data/moneymaker_llm/v3/val.jsonl` (SHA-256: `2f185914f9a790f444610534b9a2538fd0ebaf96137f09a0eeed6cc7c0c840dc`)
