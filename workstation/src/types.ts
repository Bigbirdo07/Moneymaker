export type EvidenceSource =
  | 'BROKER_LIVE'
  | 'BROKER_PAPER'
  | 'FORWARD_SHADOW'
  | 'HISTORICAL'
  | 'SIMULATED'
  | 'PROJECTED';

export type MarketStatus = 'OPEN' | 'PRE_MARKET' | 'POST_MARKET' | 'CLOSED';

export interface AccountSummary {
  account_id: string;
  equity: number;
  cash: number;
  buying_power: number;
  today_pnl: number;
  today_pnl_pct: number;
  total_realized_pnl: number;
  total_unrealized_pnl: number;
  gross_exposure: number;
  net_exposure: number;
  current_drawdown_pct: number;
  peak_equity: number;
  market_status: MarketStatus;
  broker_sync_at: string;
  market_data_sync_at: string;
  evidence_source: EvidenceSource;
}

export interface StrategyCard {
  strategy_id: string;
  strategy_name: string;
  execution_mode: string;
  authorized_capital: number;
  deployed_capital: number;
  today_pnl: number;
  cumulative_pnl: number;
  open_positions: number;
  trades_today: number;
  net_expectancy_bps: number;
  capacity_state: string;
  current_status: string;
  kill_switch_state: string;
  evidence_source: EvidenceSource;
}

export interface PositionItem {
  position_id: string;
  symbol: string;
  strategy: string;
  shares: number;
  entry_price: number;
  current_price: number;
  market_value: number;
  cost_basis: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  realized_pnl: number;
  holding_period: string;
  cohort_id?: string;
  scheduled_exit: string;
  risk_status: string;
  sector: string;
  beta: number;
  evidence_source: EvidenceSource;
}

export interface PortfolioExposure {
  by_strategy: Record<string, number>;
  by_symbol: Record<string, number>;
  by_sector: Record<string, number>;
  overnight_exposure: number;
  high_beta_exposure: number;
  cash_reserve: number;
  total_authorized: number;
}

export interface PortfolioRiskTelemetry {
  current_drawdown_pct: number;
  max_drawdown_pct: number;
  var_95_pct: number;
  var_99_pct: number;
  expected_shortfall_95_pct: number;
  expected_shortfall_99_pct: number;
  gross_exposure_usd: number;
  net_exposure_usd: number;
  combined_concentration_pct: number;
  active_portfolio_vetoes_count: number;
  portfolio_beta: number;
  stress_test_5pct_shock_usd: number;
  stress_test_10pct_crash_usd: number;
}

export interface TradeRecord {
  trade_id: string;
  strategy: string;
  symbol: string;
  signal_id: string;
  decision_id: string;
  order_id: string;
  broker_order_id: string;
  entry_timestamp: string;
  exit_timestamp?: string;
  shares: number;
  entry_price: number;
  exit_price?: number;
  gross_pnl: number;
  canonical_cost: number;
  net_pnl: number;
  return_pct: number;
  reason: string;
  evidence_source: EvidenceSource;
  is_live_verified: boolean;
}

export interface TradeExplanation {
  trade_id: string;
  symbol: string;
  strategy: string;
  signal_summary: string;
  why_selected: string;
  expected_edge: string;
  risk_checks: string[];
  execution_details: string;
  current_result: string;
  evidence_provenance: EvidenceSource;
}

export interface SignalRecord {
  signal_id: string;
  strategy: string;
  symbol: string;
  score: number;
  rank: number;
  expected_return_bps: number;
  spread_bps: number;
  estimated_friction_bps: number;
  expected_net_edge_bps: number;
  signal_status: string;
  risk_status: string;
  timestamp: string;
  evidence_source: EvidenceSource;
}

export interface MarketQuote {
  symbol: string;
  last_price: number;
  absolute_change: number;
  percent_change: number;
  bid: number;
  ask: number;
  spread_bps: number;
  volume: number;
  relative_volume: number;
  market_status: MarketStatus;
  vwap: number;
  is_data_available: boolean;
  last_updated: string;
}

export interface CandlestickBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap: number;
}

export interface StockDetail {
  symbol: string;
  name: string;
  sector: string;
  quote: MarketQuote;
  bars_1m: CandlestickBar[];
  bars_5m: CandlestickBar[];
  bars_1d: CandlestickBar[];
  alpha_a_score?: number;
  alpha_b_score?: number;
  alpha_a_rank?: number;
  alpha_b_rank?: number;
  active_position?: PositionItem;
  recent_trades: TradeRecord[];
  risk_flags: string[];
  event_flags: string[];
}

export interface CopilotChatResponse {
  reply: string;
  tool_calls: Array<{
    tool_name: string;
    parameters: Record<string, any>;
    result: any;
  }>;
  evidence_badge: EvidenceSource;
  suggested_followups: string[];
}

export interface DailyBrief {
  brief_type: string;
  generated_at: string;
  market_status: string;
  summary_bullets: string[];
  pnl_summary: string;
  strategy_activity: Record<string, string>;
  risk_and_alerts: string[];
  upcoming_events: string[];
}

export interface LiveEvidenceAuditRecord {
  record_id: string;
  table: string;
  strategy_id: string;
  broker_order_id?: string;
  timestamp: string;
  market_session_date: string;
  claimed_evidence: EvidenceSource;
  audit_status: string;
  audit_message: string;
}

export interface LiveEvidenceAuditSummary {
  total_records_inspected: number;
  verified_live_count: number;
  unverified_count: number;
  invalid_count: number;
  overall_status: string;
  audit_timestamp: string;
  details: LiveEvidenceAuditRecord[];
}

export interface SystemStatusTelemetry {
  broker_connection: string;
  broker_reconciliation_status: string;
  market_data_connection: string;
  database_state: string;
  alpha_a_engine: string;
  alpha_b_engine: string;
  portfolio_risk_aggregator: string;
  strategy_allocator: string;
  llm_copilot_state: string;
  global_kill_switch: string;
  alpha_a_kill_switch: string;
  alpha_b_kill_switch: string;
  last_sync: string;
  last_heartbeat: string;
  git_commit_hash: string;
  active_configs: Record<string, string>;
}

export interface HpcJob {
  job_id: string;
  job_name: string;
  partition: string;
  status: string;
  runtime: string;
  nodes: number;
  cpus: number;
}

export interface ExperimentRecord {
  experiment_id: string;
  created_at: string;
  strategy_id: string;
  git_commit: string;
  dataset_hash: string;
  config_hash: string;
  code_hash: string;
  random_seed: number;
  compute_target: string;
  status: string;
  slurm_job_id?: string;
  runtime_seconds: number;
  hardware_info: Record<string, any>;
  metrics: Record<string, any>;
  artifact_paths: string[];
  manifest_path?: string;
  rejection_reason?: string;
}

export interface ResearchModelRecord {
  model_id: string;
  base_model_name: string;
  base_model_path: string;
  fine_tune_dataset_id: string;
  dataset_hash: string;
  training_config: Record<string, any>;
  checkpoint_path: string;
  benchmark_score: number;
  benchmark_details: Record<string, any>;
  created_at: string;
  approval_state: string;
  provenance_state?: string;
  approval_notes?: string;
  is_workstation_active: boolean;
}

export interface DatasetManifest {
  dataset_id: string;
  symbols: string[];
  start_date: string;
  end_date: string;
  bar_frequency: string;
  source_provider: string;
  adjustment_status: string;
  feature_columns: string[];
  target_column: string;
  row_count: number;
  created_at: string;
  dataset_hash: string;
  training_cutoff_date?: string;
  embargo_bars: number;
}

export interface ResearchDocument {
  document_id: string;
  document_type: string;
  title: string;
  created_at: string;
  strategy?: string;
  phase?: string;
  evidence_type: string;
  source: string;
  hash: string;
  content: string;
}

export interface CopilotABCompareResponse {
  prompt: string;
  base_response: CopilotChatResponse;
  mmrm_response: CopilotChatResponse;
  rag_context?: string;
}

export interface FourWayBenchmarkMatrix {
  comparison_matrix: {
    Base_Only: {
      overall_score: number;
      tool_accuracy: number;
      hallucination_rate: number;
      provenance_accuracy: number;
    };
    Base_Plus_RAG: {
      overall_score: number;
      tool_accuracy: number;
      hallucination_rate: number;
      provenance_accuracy: number;
    };
    MMRM_Only: {
      overall_score: number;
      tool_accuracy: number;
      hallucination_rate: number;
      provenance_accuracy: number;
    };
    MMRM_Plus_RAG: {
      overall_score: number;
      tool_accuracy: number;
      hallucination_rate: number;
      provenance_accuracy: number;
    };
  };
  statistical_significance: {
    mcnemar_p_value_base_vs_mmrm: number;
    bootstrap_delta_ci_95: [number, number];
    verdict: string;
  };
}


