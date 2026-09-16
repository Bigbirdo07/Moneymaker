"""
Moneymaker Model Registry.
Tracks base models, LoRA/QLoRA adapter weights, benchmark evaluations,
and multi-stage governance approval states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import os
from typing import Any, Dict, List, Optional


class ModelApprovalState(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


@dataclass
class ResearchModelRecord:
    model_id: str
    base_model_name: str
    base_model_path: str
    fine_tune_dataset_id: str
    dataset_hash: str
    training_config: Dict[str, Any]
    checkpoint_path: str
    benchmark_score: float
    benchmark_details: Dict[str, Any]
    created_at: str
    approval_state: ModelApprovalState = ModelApprovalState.EXPERIMENTAL
    approval_notes: Optional[str] = None
    is_workstation_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "base_model_name": self.base_model_name,
            "base_model_path": self.base_model_path,
            "fine_tune_dataset_id": self.fine_tune_dataset_id,
            "dataset_hash": self.dataset_hash,
            "training_config": self.training_config,
            "checkpoint_path": self.checkpoint_path,
            "benchmark_score": self.benchmark_score,
            "benchmark_details": self.benchmark_details,
            "created_at": self.created_at,
            "approval_state": self.approval_state.value,
            "approval_notes": self.approval_notes,
            "is_workstation_active": self.is_workstation_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResearchModelRecord:
        return cls(
            model_id=data["model_id"],
            base_model_name=data["base_model_name"],
            base_model_path=data["base_model_path"],
            fine_tune_dataset_id=data["fine_tune_dataset_id"],
            dataset_hash=data["dataset_hash"],
            training_config=data["training_config"],
            checkpoint_path=data["checkpoint_path"],
            benchmark_score=data["benchmark_score"],
            benchmark_details=data["benchmark_details"],
            created_at=data["created_at"],
            approval_state=ModelApprovalState(data["approval_state"]),
            approval_notes=data.get("approval_notes"),
            is_workstation_active=data.get("is_workstation_active", False),
        )


class ModelRegistry:
    """
    Registry managing fine-tuned research models and checkpoint governance.
    """

    def __init__(self, storage_path: str = "outputs/models/model_registry.json") -> None:
        self.storage_path = storage_path
        self._models: Dict[str, ResearchModelRecord] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        rec = ResearchModelRecord.from_dict(item)
                        self._models[rec.model_id] = rec
                return
            except Exception:
                pass

        # Register baseline models
        self.register_model(
            model_id="BASE-QWEN-2.5-14B",
            base_model_name="Qwen2.5-14B-Instruct",
            base_model_path="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8",
            fine_tune_dataset_id="NONE_BASE",
            dataset_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            training_config={"type": "BASE_PRETRAINED"},
            checkpoint_path="BASE",
            benchmark_score=78.5,
            benchmark_details={"tool_selection": 82.0, "trade_reasoning": 75.0, "risk_comprehension": 78.5},
            approval_state=ModelApprovalState.VALIDATED,
            is_workstation_active=True,
        )

        self.register_model(
            model_id="MMRM-0.1-QLORA",
            base_model_name="Qwen2.5-14B-Instruct",
            base_model_path="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8",
            fine_tune_dataset_id="DS_MM_LLM_V1",
            dataset_hash="7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a",
            training_config={"method": "QLoRA", "lora_r": 16, "lora_alpha": 32, "lr": 2e-4, "epochs": 3},
            checkpoint_path="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/outputs/MMRM_0_1/adapter",
            benchmark_score=94.2,
            benchmark_details={"tool_selection": 96.5, "trade_reasoning": 93.0, "risk_comprehension": 94.8, "provenance_accuracy": 98.0},
            approval_state=ModelApprovalState.CANDIDATE,
            is_workstation_active=False,
        )

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump([m.to_dict() for m in self._models.values()], f, indent=2)

    def register_model(
        self,
        model_id: str,
        base_model_name: str,
        base_model_path: str,
        fine_tune_dataset_id: str,
        dataset_hash: str,
        training_config: Dict[str, Any],
        checkpoint_path: str,
        benchmark_score: float,
        benchmark_details: Dict[str, Any],
        approval_state: ModelApprovalState = ModelApprovalState.EXPERIMENTAL,
        approval_notes: Optional[str] = None,
        is_workstation_active: bool = False,
    ) -> ResearchModelRecord:
        rec = ResearchModelRecord(
            model_id=model_id,
            base_model_name=base_model_name,
            base_model_path=base_model_path,
            fine_tune_dataset_id=fine_tune_dataset_id,
            dataset_hash=dataset_hash,
            training_config=training_config,
            checkpoint_path=checkpoint_path,
            benchmark_score=benchmark_score,
            benchmark_details=benchmark_details,
            created_at=datetime.now(timezone.utc).isoformat(),
            approval_state=approval_state,
            approval_notes=approval_notes,
            is_workstation_active=is_workstation_active,
        )
        self._models[model_id] = rec
        self.save()
        return rec

    def list_models(self) -> List[ResearchModelRecord]:
        return list(self._models.values())

    def get_model(self, model_id: str) -> Optional[ResearchModelRecord]:
        return self._models.get(model_id)
