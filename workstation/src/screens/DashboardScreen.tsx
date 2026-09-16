import React, { useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  ShieldCheck,
  Activity,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { AccountSummary, StrategyCard, TradeRecord } from '../types';
import { EvidenceBadge } from '../components/EvidenceBadge';

interface Props {
  account: AccountSummary | null;
  strategies: StrategyCard[];
  trades: TradeRecord[];
}

export const DashboardScreen: React.FC<Props> = ({ account, strategies, trades }) => {
  const [timeframe, setTimeframe] = useState<'1D' | '5D' | '1M' | '3M' | 'ALL'>('1D');

  const equity = account?.equity ?? 16576.0;
  const cash = account?.cash ?? 6096.0;
  const todayPnl = account?.today_pnl ?? 142.5;
  const todayPnlPct = account?.today_pnl_pct ?? 0.87;
  const totalRealized = account?.total_realized_pnl ?? 1576.0;
  const totalUnrealized = account?.total_unrealized_pnl ?? 85.2;
  const grossExposure = account?.gross_exposure ?? 10480.0;
  const maxDrawdown = account?.current_drawdown_pct ?? 1.30;

  // Mock live activity events
  const activityEvents = [
    {
      time: '11:35:00',
      type: 'ORDER_FILLED',
      strategy: 'ALPHA_A',
      desc: 'NVDA exit filled 15 shares @ $128.50 (-$11.22 net).',
      badge: 'FILLED',
      color: 'text-amber-400',
    },
    {
      time: '11:15:00',
      type: 'SIGNAL_CREATED',
      strategy: 'ALPHA_A',
      desc: 'NVDA 15m breakout signal triggered (Score +0.845).',
      badge: 'SIGNAL',
      color: 'text-cyan-400',
    },
    {
      time: '10:05:00',
      type: 'ORDER_FILLED',
      strategy: 'ALPHA_A',
      desc: 'AMD round-trip closed 10 shares @ $154.10 (+$16.42 net).',
      badge: 'FILLED',
      color: 'text-emerald-400',
    },
    {
      time: '09:30:00',
      type: 'POSITION_OPENED',
      strategy: 'ALPHA_B',
      desc: 'AAPL Cohort #52 Entry filled 6 shares @ $224.50.',
      badge: 'COHORT',
      color: 'text-blue-400',
    },
    {
      time: '09:30:00',
      type: 'POSITION_CLOSED',
      strategy: 'ALPHA_B',
      desc: 'TSLA Cohort #49 exit completed @ $232.50 (+$83.72 net).',
      badge: 'EXIT',
      color: 'text-emerald-400',
    },
    {
      time: '09:28:00',
      type: 'RISK_VETO',
      strategy: 'PORTFOLIO',
      desc: 'PortfolioRiskAggregator intercepted GOOGL opening size (Capped).',
      badge: 'VETO',
      color: 'text-rose-400',
    },
  ];

  return (
    <div className="space-y-6">
      {/* 1. TOP KPI TILES */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] font-mono text-gray-400 uppercase flex items-center justify-between">
            <span>Account Equity</span>
            <EvidenceBadge source="BROKER_LIVE" />
          </div>
          <div className="text-xl font-bold font-mono text-white tracking-tight">
            ${equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-emerald-400 flex items-center gap-0.5">
            <ArrowUpRight className="w-3 h-3" />
            +${todayPnl.toFixed(2)} (+{todayPnlPct.toFixed(2)}%)
          </div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] font-mono text-gray-400 uppercase">Cash & Buying Power</div>
          <div className="text-xl font-bold font-mono text-cyan-300 tracking-tight">
            ${cash.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-gray-400">100% Cash / Zero Margin</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] font-mono text-gray-400 uppercase">Realized P&L</div>
          <div className="text-xl font-bold font-mono text-emerald-400 tracking-tight">
            +${totalRealized.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-gray-400">Cumulative Multi-Strategy</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] font-mono text-gray-400 uppercase">Unrealized P&L</div>
          <div className="text-xl font-bold font-mono text-emerald-300 tracking-tight">
            +${totalUnrealized.toFixed(2)}
          </div>
          <div className="text-[11px] font-mono text-gray-400">Across Active Positions</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] font-mono text-gray-400 uppercase">Gross Exposure</div>
          <div className="text-xl font-bold font-mono text-white tracking-tight">
            ${grossExposure.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-gray-400">69.87% Capital Utilized</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] font-mono text-gray-400 uppercase">Max Drawdown</div>
          <div className="text-xl font-bold font-mono text-emerald-400 tracking-tight">
            {maxDrawdown.toFixed(2)}%
          </div>
          <div className="text-[11px] font-mono text-gray-400">Peak DD: $195.00 USD</div>
        </div>
      </div>

      {/* 2. STRATEGY CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {strategies.map((strat) => {
          const isAlphaA = strat.strategy_id.includes('ALPHA_A');
          return (
            <div
              key={strat.strategy_id}
              className="glass-panel p-4 space-y-4 border-l-4 border-l-cyan-500 glass-panel-hover"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-bold text-white flex items-center gap-2">
                    {strat.strategy_name}
                    <EvidenceBadge source={strat.evidence_source} />
                  </div>
                  <div className="text-[11px] font-mono text-gray-400">
                    Mode: {strat.execution_mode}
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold">
                  {strat.current_status}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                <div className="p-2 rounded bg-white/[0.02] border border-white/5">
                  <div className="text-gray-400 text-[10px]">AUTH CAPITAL</div>
                  <div className="font-bold text-white">${strat.authorized_capital.toLocaleString()}</div>
                </div>
                <div className="p-2 rounded bg-white/[0.02] border border-white/5">
                  <div className="text-gray-400 text-[10px]">DEPLOYED</div>
                  <div className="font-bold text-cyan-400">${strat.deployed_capital.toFixed(2)}</div>
                </div>
                <div className="p-2 rounded bg-white/[0.02] border border-white/5">
                  <div className="text-gray-400 text-[10px]">NET EXPECTANCY</div>
                  <div className="font-bold text-emerald-400">+{strat.net_expectancy_bps.toFixed(3)} bps</div>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs font-mono pt-2 border-t border-white/5">
                <span className="text-gray-400">
                  Cumulative P&L: <strong className="text-emerald-400">+${strat.cumulative_pnl.toFixed(2)}</strong>
                </span>
                <span className="text-gray-400">
                  Open: <strong className="text-white">{strat.open_positions} positions</strong> | Trades Today: <strong className="text-white">{strat.trades_today}</strong>
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 3. PORTFOLIO EQUITY CHART & LIVE FEED */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Equity Chart (2 cols) */}
        <div className="lg:col-span-2 glass-panel p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                Portfolio Equity Curve
                <span className="text-[10px] font-mono text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-500/30">
                  Sharpe 7.67
                </span>
              </div>
              <div className="text-xs text-gray-400 font-mono">
                Historical & Intraday Equity Growth ($15,000 Authorized Basis)
              </div>
            </div>

            <div className="flex items-center gap-1 bg-white/[0.04] p-1 rounded border border-white/5 font-mono text-[11px]">
              {(['1D', '5D', '1M', '3M', 'ALL'] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-2 py-0.5 rounded ${
                    timeframe === tf
                      ? 'bg-cyan-500 text-black font-bold'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>

          {/* SVG Line Chart */}
          <div className="h-64 w-full relative pt-2">
            <svg className="w-full h-full" viewBox="0 0 600 200" preserveAspectRatio="none">
              <defs>
                <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00f2fe" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#00f2fe" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              {/* Grid Lines */}
              <line x1="0" y1="50" x2="600" y2="50" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
              <line x1="0" y1="100" x2="600" y2="100" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
              <line x1="0" y1="150" x2="600" y2="150" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />

              {/* Area Fill */}
              <polygon
                points="0,180 50,165 100,160 150,145 200,135 250,140 300,110 350,95 400,85 450,60 500,45 550,30 600,20 600,200 0,200"
                fill="url(#equityGrad)"
              />
              {/* Line */}
              <polyline
                points="0,180 50,165 100,160 150,145 200,135 250,140 300,110 350,95 400,85 450,60 500,45 550,30 600,20"
                fill="none"
                stroke="#00f2fe"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </svg>

            <div className="flex justify-between text-[10px] font-mono text-gray-500 mt-1">
              <span>09:30 EST</span>
              <span>11:00</span>
              <span>12:30</span>
              <span>14:00</span>
              <span>16:00 EST</span>
            </div>
          </div>
        </div>

        {/* Live Activity Feed (1 col) */}
        <div className="glass-panel p-4 space-y-3 flex flex-col justify-between">
          <div>
            <div className="text-sm font-bold text-white flex items-center justify-between">
              <span>Live Execution Feed</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-green" />
            </div>
            <div className="text-xs text-gray-400 font-mono">Real-time order & risk events</div>
          </div>

          <div className="space-y-2.5 overflow-y-auto max-h-56 pr-1 font-mono text-xs">
            {activityEvents.map((evt, i) => (
              <div
                key={i}
                className="p-2 rounded bg-white/[0.02] border border-white/5 space-y-0.5 hover:border-white/10 transition-colors"
              >
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-gray-400 flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    {evt.time}
                  </span>
                  <span className={`font-bold ${evt.color}`}>{evt.badge}</span>
                </div>
                <div className="text-gray-200 text-[11px] leading-tight">{evt.desc}</div>
              </div>
            ))}
          </div>

          <div className="text-[10px] font-mono text-gray-500 text-center border-t border-white/5 pt-2">
            Deterministic Risk Aggregator Active (0 Unresolved Breaks)
          </div>
        </div>
      </div>
    </div>
  );
};
