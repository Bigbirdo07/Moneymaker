import {
  AccountSummary,
  DailyBrief,
  LiveEvidenceAuditSummary,
  MarketQuote,
  PortfolioExposure,
  PortfolioRiskTelemetry,
  PositionItem,
  StockDetail,
  StrategyCard,
  SystemStatusTelemetry,
  TradeExplanation,
  TradeRecord,
  CopilotChatResponse,
} from './types';

const API_BASE = '/api';

export const api = {
  async getAccount(): Promise<AccountSummary> {
    const res = await fetch(`${API_BASE}/account`);
    if (!res.ok) throw new Error('Failed to fetch account');
    return res.json();
  },

  async getPortfolioExposure(): Promise<PortfolioExposure> {
    const res = await fetch(`${API_BASE}/portfolio/exposure`);
    if (!res.ok) throw new Error('Failed to fetch portfolio exposure');
    return res.json();
  },

  async getPositions(): Promise<PositionItem[]> {
    const res = await fetch(`${API_BASE}/positions`);
    if (!res.ok) throw new Error('Failed to fetch positions');
    return res.json();
  },

  async getTrades(): Promise<TradeRecord[]> {
    const res = await fetch(`${API_BASE}/trades`);
    if (!res.ok) throw new Error('Failed to fetch trades');
    return res.json();
  },

  async explainTrade(tradeId: string): Promise<TradeExplanation> {
    const res = await fetch(`${API_BASE}/trades/${encodeURIComponent(tradeId)}/explain`);
    if (!res.ok) throw new Error('Failed to explain trade');
    return res.json();
  },

  async getStrategies(): Promise<StrategyCard[]> {
    const res = await fetch(`${API_BASE}/strategies`);
    if (!res.ok) throw new Error('Failed to fetch strategies');
    return res.json();
  },

  async getStrategySignals(strategyId: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/strategies/${encodeURIComponent(strategyId)}/signals`);
    if (!res.ok) throw new Error('Failed to fetch strategy signals');
    return res.json();
  },

  async getRisk(): Promise<PortfolioRiskTelemetry> {
    const res = await fetch(`${API_BASE}/risk`);
    if (!res.ok) throw new Error('Failed to fetch risk');
    return res.json();
  },

  async getRiskVetoes(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/risk/vetoes`);
    if (!res.ok) throw new Error('Failed to fetch risk vetoes');
    return res.json();
  },

  async getWatchlist(): Promise<MarketQuote[]> {
    const res = await fetch(`${API_BASE}/market/watchlist`);
    if (!res.ok) throw new Error('Failed to fetch watchlist');
    return res.json();
  },

  async getStockDetail(symbol: string): Promise<StockDetail> {
    const res = await fetch(`${API_BASE}/market/${encodeURIComponent(symbol)}/detail`);
    if (!res.ok) throw new Error(`Failed to fetch detail for ${symbol}`);
    return res.json();
  },

  async getDailyBrief(briefType: string): Promise<DailyBrief> {
    const res = await fetch(`${API_BASE}/briefs/${encodeURIComponent(briefType)}`);
    if (!res.ok) throw new Error(`Failed to fetch ${briefType} brief`);
    return res.json();
  },

  async getSystemStatus(): Promise<SystemStatusTelemetry> {
    const res = await fetch(`${API_BASE}/system`);
    if (!res.ok) throw new Error('Failed to fetch system telemetry');
    return res.json();
  },

  async getProvenanceAudit(): Promise<LiveEvidenceAuditSummary> {
    const res = await fetch(`${API_BASE}/provenance/audit`);
    if (!res.ok) throw new Error('Failed to audit live evidence');
    return res.json();
  },

  async chatCopilot(message: string, contextTradeId?: string): Promise<CopilotChatResponse> {
    const res = await fetch(`${API_BASE}/copilot/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, context_trade_id: contextTradeId }),
    });
    if (!res.ok) throw new Error('Copilot query failed');
    return res.json();
  },
};
