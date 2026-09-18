import {
  AccountSummary,
  DailyBrief,
  DatasetManifest,
  ExperimentRecord,
  FourWayBenchmarkMatrix,
  HpcJob,
  LiveEvidenceAuditSummary,
  MarketQuote,
  PortfolioExposure,
  PortfolioRiskTelemetry,
  PositionItem,
  ResearchDocument,
  ResearchModelRecord,
  StockDetail,
  StrategyCard,
  SystemStatusTelemetry,
  TradeExplanation,
  TradeRecord,
  CopilotChatResponse,
  CopilotABCompareResponse,
  CopilotAuditSummary,
  CopilotModelInfo,
  ResearchProposal,
  CopilotInteractionRecord,
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

  // Research & Unity HPC
  async getResearchJobs(): Promise<HpcJob[]> {
    const res = await fetch(`${API_BASE}/research/jobs`);
    if (!res.ok) throw new Error('Failed to fetch research jobs');
    return res.json();
  },

  async submitResearchJob(payload: {
    slurm_template: string;
    experiment_id?: string;
    config_path?: string;
    compute_target?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/research/jobs/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to submit research job');
    return res.json();
  },

  async cancelResearchJob(jobId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/research/jobs/${encodeURIComponent(jobId)}/cancel`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Failed to cancel job ${jobId}`);
    return res.json();
  },

  async getResearchJobLogs(jobId: string): Promise<{ job_id: string; logs: string }> {
    const res = await fetch(`${API_BASE}/research/jobs/${encodeURIComponent(jobId)}/logs`);
    if (!res.ok) throw new Error(`Failed to fetch logs for job ${jobId}`);
    return res.json();
  },

  async getResearchExperiments(): Promise<ExperimentRecord[]> {
    const res = await fetch(`${API_BASE}/research/experiments`);
    if (!res.ok) throw new Error('Failed to fetch experiments');
    return res.json();
  },

  async getResearchModels(): Promise<ResearchModelRecord[]> {
    const res = await fetch(`${API_BASE}/research/models`);
    if (!res.ok) throw new Error('Failed to fetch models');
    return res.json();
  },

  async getResearchDatasets(): Promise<DatasetManifest[]> {
    const res = await fetch(`${API_BASE}/research/datasets`);
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async getResearchMemory(query: string = ''): Promise<ResearchDocument[]> {
    const res = await fetch(`${API_BASE}/research/memory?query=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to query research memory');
    return res.json();
  },

  async auditModelProvenance(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/research/models/${encodeURIComponent(modelId)}/audit`);
    if (!res.ok) throw new Error(`Failed to audit provenance for ${modelId}`);
    return res.json();
  },

  async get4WayBenchmark(): Promise<FourWayBenchmarkMatrix> {
    const res = await fetch(`${API_BASE}/research/benchmark/4way`);
    if (!res.ok) throw new Error('Failed to fetch 4-way benchmark matrix');
    return res.json();
  },

  async compareCopilotAB(prompt: string): Promise<CopilotABCompareResponse> {
    const res = await fetch(`${API_BASE}/copilot/ab_compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error('Failed to run Copilot A/B comparison');
    return res.json();
  },

  async submitCopilotFeedback(payload: {
    prompt: string;
    winner: string;
    notes?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/copilot/ab_feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to submit Copilot feedback');
    return res.json();
  },

  async voteCopilotAB(payload: {
    interaction_id: string;
    preference: string;
    reason_tags?: string[];
    notes?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/copilot/ab/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to submit vote');
    return res.json();
  },

  async getCopilotAudit(): Promise<CopilotAuditSummary> {
    const res = await fetch(`${API_BASE}/copilot/ab/audit`);
    if (!res.ok) throw new Error('Failed to fetch Copilot A/B audit');
    return res.json();
  },

  async getCopilotDailySummary(): Promise<DailyBrief> {
    const res = await fetch(`${API_BASE}/copilot/daily_summary`);
    if (!res.ok) throw new Error('Failed to fetch daily summary');
    return res.json();
  },

  async getCopilotModels(): Promise<CopilotModelInfo[]> {
    const res = await fetch(`${API_BASE}/copilot/models`);
    if (!res.ok) throw new Error('Failed to fetch Copilot models');
    return res.json();
  },

  async proposeResearchExperiment(query: string): Promise<{ success: boolean; proposal: ResearchProposal }> {
    const res = await fetch(`${API_BASE}/research/experiments/propose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error('Failed to propose research experiment');
    return res.json();
  },
};


