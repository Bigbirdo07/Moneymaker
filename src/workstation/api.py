"""
Moneymaker Workstation REST & WebSocket API Router.
Provides structured, type-safe endpoints for the React/TypeScript frontend
and strictly isolates execution layers from unauthorized write requests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.research.dataset_versioning import DatasetRegistry
from src.research.experiment_registry import ComputeTarget, ExperimentRegistry
from src.research.model_registry import ModelRegistry
from src.research.research_memory import ResearchMemory
from src.research.unity_client import UnityHPCClient
from src.workstation.copilot_engine import MoneymakerCopilotEngine
from src.workstation.copilot_tools import CopilotToolRegistry

from src.workstation.models import (
    AccountSummary,
    CopilotChatRequest,
    CopilotChatResponse,
    DailyBrief,
    LiveEvidenceAuditSummary,
    MarketQuote,
    PositionItem,
    PortfolioExposure,
    PortfolioRiskTelemetry,
    StockDetail,
    StrategyCard,
    SystemStatusTelemetry,
    TradeExplanation,
    TradeRecord,
)
from src.workstation.provenance import DataProvenanceEngine
from src.workstation.service import WorkstationService
from src.workstation.streaming import streaming_hub


def create_workstation_app() -> FastAPI:
    """Factory creating configured FastAPI workstation application."""
    app = FastAPI(
        title="Moneymaker Workstation API",
        description="Local-First Trading & Research Workstation API",
        version="1.0.0",
    )

    # Enable CORS for local Vite development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    service = WorkstationService()
    tool_registry = CopilotToolRegistry(service=service)
    copilot_engine = MoneymakerCopilotEngine(tool_registry=tool_registry)

    # =================================================================
    # ACCOUNT & PORTFOLIO ENDPOINTS
    # =================================================================

    @app.get("/api/account", response_model=AccountSummary)
    def get_account() -> AccountSummary:
        return service.get_account_summary()

    @app.get("/api/portfolio/exposure", response_model=PortfolioExposure)
    def get_portfolio_exposure() -> PortfolioExposure:
        return service.get_portfolio_exposure()

    @app.get("/api/positions", response_model=List[PositionItem])
    def get_positions() -> List[PositionItem]:
        return service.get_positions()

    @app.get("/api/positions/{symbol}", response_model=PositionItem)
    def get_position(symbol: str) -> PositionItem:
        pos = service.get_position(symbol)
        if not pos:
            raise HTTPException(status_code=404, detail=f"No active position in {symbol.upper()}")
        return pos

    # =================================================================
    # TRADES & EXPLANATION ENDPOINTS
    # =================================================================

    @app.get("/api/trades", response_model=List[TradeRecord])
    def get_trades() -> List[TradeRecord]:
        return service.get_trades()

    @app.get("/api/trades/{trade_id}", response_model=TradeRecord)
    def get_trade(trade_id: str) -> TradeRecord:
        trd = service.get_trade(trade_id)
        if not trd:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        return trd

    @app.get("/api/trades/{trade_id}/explain", response_model=TradeExplanation)
    def explain_trade(trade_id: str) -> TradeExplanation:
        return service.explain_trade(trade_id)

    # =================================================================
    # STRATEGY & SIGNAL ENDPOINTS
    # =================================================================

    @app.get("/api/strategies", response_model=List[StrategyCard])
    def get_strategies() -> List[StrategyCard]:
        return service.get_strategy_cards()

    @app.get("/api/strategies/{strategy_id}/signals")
    def get_strategy_signals(strategy_id: str) -> List[Dict[str, Any]]:
        s_id = strategy_id.upper()
        if "ALPHA_A" in s_id:
            return [s.model_dump() for s in service.get_alpha_a_signals()]
        elif "ALPHA_B" in s_id:
            return [s.model_dump() for s in service.get_alpha_b_signals()]
        return []

    @app.get("/api/strategies/{strategy_id}/health")
    def get_strategy_health(strategy_id: str) -> Dict[str, Any]:
        return tool_registry.get_strategy_health(strategy_id)

    @app.get("/api/strategies/{strategy_id}/capacity")
    def get_strategy_capacity(strategy_id: str) -> Dict[str, Any]:
        return tool_registry.get_strategy_capacity(strategy_id)

    # =================================================================
    # RISK ENDPOINTS
    # =================================================================

    @app.get("/api/risk", response_model=PortfolioRiskTelemetry)
    def get_portfolio_risk() -> PortfolioRiskTelemetry:
        return service.get_portfolio_risk()

    @app.get("/api/risk/vetoes")
    def get_risk_vetoes() -> List[Dict[str, Any]]:
        return tool_registry.get_recent_risk_vetoes()

    # =================================================================
    # MARKET DATA ENDPOINTS
    # =================================================================

    @app.get("/api/market/watchlist", response_model=List[MarketQuote])
    def get_watchlist() -> List[MarketQuote]:
        return service.get_watchlist()

    @app.get("/api/market/{symbol}", response_model=MarketQuote)
    def get_quote(symbol: str) -> MarketQuote:
        return service.get_live_quote(symbol)

    @app.get("/api/market/{symbol}/detail", response_model=StockDetail)
    def get_stock_detail(symbol: str) -> StockDetail:
        return service.get_stock_detail(symbol)

    # =================================================================
    # BRIEFS & SYSTEM & PROVENANCE
    # =================================================================

    @app.get("/api/briefs/{brief_type}", response_model=DailyBrief)
    def get_brief(brief_type: str) -> DailyBrief:
        return service.get_daily_brief(brief_type)

    @app.get("/api/system", response_model=SystemStatusTelemetry)
    def get_system_status() -> SystemStatusTelemetry:
        return service.get_system_status()

    @app.get("/api/provenance/audit", response_model=LiveEvidenceAuditSummary)
    def audit_provenance() -> LiveEvidenceAuditSummary:
        raw_trades = [t.model_dump() for t in service.get_trades()]
        return DataProvenanceEngine.audit_live_evidence(raw_trades)

    # =================================================================
    # AI COPILOT ENDPOINTS
    # =================================================================

    @app.post("/api/copilot/chat", response_model=CopilotChatResponse)
    def copilot_chat(request: CopilotChatRequest) -> CopilotChatResponse:
        return copilot_engine.handle_message(request)

    @app.post("/api/copilot/tool")
    def execute_copilot_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = payload.get("tool_name", "")
        params = payload.get("parameters", {})
        return tool_registry.execute_tool(tool_name, params)

    # =================================================================
    # RESEARCH & UNITY HPC ENDPOINTS
    # =================================================================

    unity_client = UnityHPCClient()
    exp_registry = ExperimentRegistry()
    model_registry = ModelRegistry()
    dataset_registry = DatasetRegistry()
    research_memory = ResearchMemory()

    @app.get("/api/research/jobs")
    def get_research_jobs() -> List[Dict[str, Any]]:
        return unity_client.list_jobs()

    @app.post("/api/research/jobs/submit")
    def submit_research_job(payload: Dict[str, Any]) -> Dict[str, Any]:
        template = payload.get("slurm_template", "jobs/cpu_backtest.slurm")
        experiment_id = payload.get("experiment_id", f"EXP_USER_{int(datetime.now(timezone.utc).timestamp())}")
        config_path = payload.get("config_path", "configs/research_default.json")
        target_str = payload.get("compute_target", "UNITY_GPU")
        try:
            target = ComputeTarget(target_str)
        except Exception:
            target = ComputeTarget.UNITY_GPU
        return unity_client.submit_job(
            slurm_template=template,
            experiment_id=experiment_id,
            config_path=config_path,
            compute_target=target,
        )

    @app.post("/api/research/jobs/{job_id}/cancel")
    def cancel_research_job(job_id: str) -> Dict[str, Any]:
        return unity_client.cancel_job(job_id)

    @app.get("/api/research/jobs/{job_id}/logs")
    def get_research_job_logs(job_id: str) -> Dict[str, Any]:
        logs = unity_client.fetch_logs(job_id)
        return {"job_id": job_id, "logs": logs}

    @app.get("/api/research/experiments")
    def get_research_experiments() -> List[Dict[str, Any]]:
        return [e.to_dict() for e in exp_registry.list_experiments()]

    @app.get("/api/research/models")
    def get_research_models() -> List[Dict[str, Any]]:
        return [m.to_dict() for m in model_registry.list_models()]

    @app.get("/api/research/datasets")
    def get_research_datasets() -> List[Dict[str, Any]]:
        return [d.to_dict() for d in dataset_registry.list_manifests()]

    @app.get("/api/research/memory")
    def get_research_memory(query: str = "") -> List[Dict[str, Any]]:
        return [d.to_dict() for d in research_memory.search(query)]

    # =================================================================
    # WEBSOCKET STREAMING
    # =================================================================

    @app.websocket("/ws/stream")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await streaming_hub.connect(websocket)
        try:
            while True:
                # Keep alive / listen for client pings
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            streaming_hub.disconnect(websocket)
        except Exception:
            streaming_hub.disconnect(websocket)

    return app


app = create_workstation_app()

