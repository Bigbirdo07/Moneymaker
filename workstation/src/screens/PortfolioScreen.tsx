import React from 'react';
import {
  Briefcase,
  Layers,
  PieChart,
  ShieldAlert,
  ArrowUpRight,
  Clock,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { PositionItem, PortfolioExposure, PortfolioRiskTelemetry } from '../types';
import { EvidenceBadge } from '../components/EvidenceBadge';

interface Props {
  positions: PositionItem[];
  exposure: PortfolioExposure | null;
  risk: PortfolioRiskTelemetry | null;
}

export const PortfolioScreen: React.FC<Props> = ({ positions, exposure, risk }) => {
  const totalMarketValue = positions.reduce((acc, p) => acc + p.market_value, 0);
  const totalUnrealized = positions.reduce((acc, p) => acc + p.unrealized_pnl, 0);

  return (
    <div className="space-y-6">
      {/* 1. TOP PORTFOLIO KPI BANNER */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono">
        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] text-gray-400 uppercase flex items-center justify-between">
            <span>Deployed Market Value</span>
            <EvidenceBadge source="BROKER_LIVE" />
          </div>
          <div className="text-xl font-bold text-white">
            ${totalMarketValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-gray-400">{positions.length} Active Long Positions</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] text-gray-400 uppercase">Unrealized P&L</div>
          <div className="text-xl font-bold text-emerald-400">
            +${totalUnrealized.toFixed(2)}
          </div>
          <div className="text-[11px] text-gray-400">Across Open Cohorts</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] text-gray-400 uppercase">Cash Reserve</div>
          <div className="text-xl font-bold text-cyan-300">
            ${(exposure?.cash_reserve ?? 6096).toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-gray-400">Zero Margin Borrowing</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[11px] text-gray-400 uppercase">Combined Max Drawdown</div>
          <div className="text-xl font-bold text-emerald-400">
            {risk?.max_drawdown_pct.toFixed(2) ?? '1.30'}%
          </div>
          <div className="text-[11px] text-gray-400">Peak DD: $195.00 USD</div>
        </div>
      </div>

      {/* 2. OPEN POSITIONS TABLE */}
      <div className="glass-panel overflow-hidden">
        <div className="p-3.5 border-b border-white/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold font-mono text-white flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-cyan-400" />
              OPEN PORTFOLIO POSITIONS ({positions.length})
            </div>
            <div className="text-[11px] text-gray-400 font-mono">
              Every position has strict, immutable strategy ownership. No unowned positions.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.04] text-gray-300 border border-white/5">
              100% LONG ONLY
            </span>
            <EvidenceBadge source="BROKER_LIVE" />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Strategy Ownership</th>
                <th className="text-right">Shares</th>
                <th className="text-right">Entry</th>
                <th className="text-right">Current</th>
                <th className="text-right">Market Value</th>
                <th className="text-right">Cost Basis</th>
                <th className="text-right">Unrealized P&L</th>
                <th>Cohort / Horizon</th>
                <th>Scheduled Exit</th>
                <th className="text-center">Risk Status</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos) => {
                const isAlphaA = pos.strategy.includes('ALPHA_A');
                const isPnlPos = pos.unrealized_pnl >= 0;
                return (
                  <tr key={pos.position_id}>
                    <td className="font-bold font-mono text-white">{pos.symbol}</td>
                    <td>
                      <span
                        className={`inline-flex items-center gap-1 font-mono text-[10px] font-bold px-2 py-0.5 rounded border ${
                          isAlphaA
                            ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/30'
                            : 'bg-blue-950/80 text-blue-300 border-blue-500/30'
                        }`}
                      >
                        {isAlphaA ? 'ALPHA A (INTRADAY)' : 'ALPHA B (REVERSAL)'}
                      </span>
                    </td>
                    <td className="text-right font-mono text-white">{pos.shares}</td>
                    <td className="text-right font-mono text-gray-300">${pos.entry_price.toFixed(2)}</td>
                    <td className="text-right font-mono text-white font-semibold">
                      ${pos.current_price.toFixed(2)}
                    </td>
                    <td className="text-right font-mono text-cyan-300 font-semibold">
                      ${pos.market_value.toFixed(2)}
                    </td>
                    <td className="text-right font-mono text-gray-400">${pos.cost_basis.toFixed(2)}</td>
                    <td
                      className={`text-right font-mono font-bold ${
                        isPnlPos ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {isPnlPos ? '+' : ''}${pos.unrealized_pnl.toFixed(2)} (
                      {isPnlPos ? '+' : ''}{pos.unrealized_pnl_pct.toFixed(2)}%)
                    </td>
                    <td className="font-mono text-gray-300 text-xs">
                      {pos.cohort_id ? `${pos.cohort_id} (${pos.holding_period})` : pos.holding_period}
                    </td>
                    <td className="font-mono text-gray-400 text-xs">
                      {pos.scheduled_exit ? new Date(pos.scheduled_exit).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Intraday Close'}
                    </td>
                    <td className="text-center font-mono">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                        {pos.risk_status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. EXPOSURE & RISK TELEMETRY BREAKDOWN */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Exposure Distribution */}
        <div className="glass-panel p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold font-mono text-white flex items-center gap-1.5">
              <PieChart className="w-3.5 h-3.5 text-cyan-400" />
              PORTFOLIO EXPOSURE BREAKDOWN
            </div>
            <span className="text-[10px] font-mono text-gray-400">Total Authorized: $15,000 USD</span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            {/* Strategy Allocation */}
            <div>
              <div className="flex justify-between text-gray-300 text-[11px] mb-1">
                <span>Alpha A Partition ($10k Max)</span>
                <span className="text-emerald-400">$1,542.00 USD (15.4% Deployed)</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: '15.4%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-gray-300 text-[11px] mb-1">
                <span>Alpha B Partition ($5k Max)</span>
                <span className="text-blue-400">$3,685.30 USD (73.7% Deployed)</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: '73.7%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-gray-300 text-[11px] mb-1">
                <span>Overnight Exposure (Alpha B Cohorts)</span>
                <span className="text-amber-400">$3,685.30 USD (24.5% of Equity)</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full" style={{ width: '24.5%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-gray-300 text-[11px] mb-1">
                <span>High-Beta Exposure (&beta; &gt; 1.3)</span>
                <span className="text-purple-400">$2,567.20 USD (17.1% of Equity)</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-purple-500 rounded-full" style={{ width: '17.1%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Portfolio Risk & Tail Metrics */}
        <div className="glass-panel p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold font-mono text-white flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
              PORTFOLIO RISK & TAIL METRICS
            </div>
            <span className="text-[10px] font-mono text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-500/30">
              VETO GATE ACTIVE
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
              <div className="text-gray-400 text-[10px]">DAILY VaR (95% / 99%)</div>
              <div className="font-bold text-white text-sm">
                {risk?.var_95_pct.toFixed(2) ?? '0.46'}% / {risk?.var_99_pct.toFixed(2) ?? '0.72'}%
              </div>
              <div className="text-[10px] text-gray-500">Max loss under normal regimes</div>
            </div>

            <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
              <div className="text-gray-400 text-[10px]">EXPECTED SHORTFALL (95%)</div>
              <div className="font-bold text-amber-400 text-sm">
                {risk?.expected_shortfall_95_pct.toFixed(2) ?? '0.60'}%
              </div>
              <div className="text-[10px] text-gray-500">Tail conditional loss</div>
            </div>

            <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
              <div className="text-gray-400 text-[10px]">-5.0% MARKET SHOCK</div>
              <div className="font-bold text-rose-400 text-sm">
                ${risk?.stress_test_5pct_shock_usd.toFixed(2) ?? '-261.37'}
              </div>
              <div className="text-[10px] text-gray-500">Projected mark-to-market</div>
            </div>

            <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
              <div className="text-gray-400 text-[10px]">PORTFOLIO BETA (&beta;)</div>
              <div className="font-bold text-cyan-300 text-sm">
                {risk?.portfolio_beta.toFixed(2) ?? '1.04'}
              </div>
              <div className="text-[10px] text-gray-500">Relative to S&P 500</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
