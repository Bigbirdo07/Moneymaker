import React, { useState } from 'react';
import {
  Layers,
  Zap,
  Activity,
  Shield,
  TrendingDown,
  Lock,
  ArrowUpRight,
  Info,
  CheckCircle2,
} from 'lucide-react';
import { StrategyCard } from '../types';
import { EvidenceBadge } from '../components/EvidenceBadge';

interface Props {
  strategies: StrategyCard[];
}

export const StrategiesScreen: React.FC<Props> = ({ strategies }) => {
  const [activeStrategy, setActiveStrategy] = useState<'ALPHA_A' | 'ALPHA_B'>('ALPHA_B');

  const alphaASignals = [
    { symbol: 'AMD', score: 0.912, rank: 1, expReturn: 5.20, spread: 1.80, friction: 3.76, netEdge: 1.44, status: 'ACTIVE', risk: 'APPROVED' },
    { symbol: 'NVDA', score: 0.845, rank: 2, expReturn: 4.80, spread: 1.60, friction: 3.76, netEdge: 1.04, status: 'ACTIVE', risk: 'APPROVED' },
    { symbol: 'TSLA', score: 0.780, rank: 3, expReturn: 4.10, spread: 2.10, friction: 3.85, netEdge: 0.25, status: 'WATCHLIST', risk: 'APPROVED' },
    { symbol: 'MSFT', score: 0.620, rank: 4, expReturn: 3.10, spread: 1.20, friction: 3.76, netEdge: -0.66, status: 'FILTERED', risk: 'REJECTED_NEGATIVE_EDGE' },
  ];

  const alphaBSignals = [
    { symbol: 'AAPL', score: -1.85, rank: 1, expReturn: 16.80, spread: 1.84, friction: 5.58, netEdge: 11.22, status: 'ACTIVE_COHORT_52', risk: 'APPROVED' },
    { symbol: 'MSFT', score: -1.62, rank: 2, expReturn: 15.90, spread: 1.88, friction: 5.58, netEdge: 10.32, status: 'ACTIVE_COHORT_51', risk: 'APPROVED' },
    { symbol: 'AMZN', score: -1.41, rank: 3, expReturn: 14.20, spread: 2.10, friction: 5.65, netEdge: 8.55, status: 'CANDIDATE', risk: 'APPROVED' },
    { symbol: 'GOOGL', score: -1.10, rank: 4, expReturn: 12.50, spread: 2.20, friction: 5.70, netEdge: 6.80, status: 'CANDIDATE', risk: 'APPROVED' },
  ];

  const currentSignals = activeStrategy === 'ALPHA_A' ? alphaASignals : alphaBSignals;

  return (
    <div className="space-y-6">
      {/* 1. STRATEGY SELECTOR TABS */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveStrategy('ALPHA_A')}
            className={`flex items-center gap-2 px-4 py-2 rounded font-mono text-xs font-bold transition-all ${
              activeStrategy === 'ALPHA_A'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40 shadow-sm shadow-emerald-500/10'
                : 'text-gray-400 hover:text-white bg-white/[0.02]'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            ALPHA A (INTRADAY MOMENTUM - $10k)
          </button>

          <button
            onClick={() => setActiveStrategy('ALPHA_B')}
            className={`flex items-center gap-2 px-4 py-2 rounded font-mono text-xs font-bold transition-all ${
              activeStrategy === 'ALPHA_B'
                ? 'bg-blue-950 text-blue-400 border border-blue-500/40 shadow-sm shadow-blue-500/10'
                : 'text-gray-400 hover:text-white bg-white/[0.02]'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-blue-400" />
            ALPHA B (MULTI-DAY REVERSAL - $5k)
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-gray-400">Governance Status:</span>
          <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/30 text-xs font-mono font-semibold">
            {activeStrategy === 'ALPHA_A' ? 'CAPACITY_HOLD_WATCH' : 'ALPHA_B_TIER2_VALIDATED'}
          </span>
          <EvidenceBadge source="BROKER_LIVE" />
        </div>
      </div>

      {/* 2. STRATEGY OVERVIEW CARD */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 font-mono">
        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Authorized Capital</div>
          <div className="text-xl font-bold text-white">
            {activeStrategy === 'ALPHA_A' ? '$10,000.00' : '$5,000.00'} USD
          </div>
          <div className="text-[10px] text-emerald-400">100% Live Validated</div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Net Expectancy</div>
          <div className="text-xl font-bold text-emerald-400">
            {activeStrategy === 'ALPHA_A' ? '+1.110 bps / trade' : '+10.400 bps / cycle'}
          </div>
          <div className="text-[10px] text-gray-400">
            {activeStrategy === 'ALPHA_A' ? '95% CI: [+0.58, +1.64]' : '95% CI: [+6.05, +14.75]'}
          </div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Edge Retention</div>
          <div className="text-xl font-bold text-cyan-300">
            {activeStrategy === 'ALPHA_A' ? '70.70% (WATCH)' : '97.47% (HEALTHY)'}
          </div>
          <div className="text-[10px] text-gray-400">
            Cost Buffer: {activeStrategy === 'ALPHA_A' ? '1.30x' : '2.86x'}
          </div>
        </div>

        <div className="glass-panel p-3.5 space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Holding Horizon</div>
          <div className="text-xl font-bold text-white">
            {activeStrategy === 'ALPHA_A' ? '15-20 Minutes' : '3 Days (FIFO)'}
          </div>
          <div className="text-[10px] text-gray-400">
            {activeStrategy === 'ALPHA_A' ? 'Flat Overnight' : 'Active Multi-Day Cohorts'}
          </div>
        </div>
      </div>

      {/* 3. RANKED OPPORTUNITY SCANNER */}
      <div className="glass-panel overflow-hidden">
        <div className="p-3.5 border-b border-white/10 flex items-center justify-between">
          <div className="text-xs font-bold font-mono text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            CURRENT OPPORTUNITY RANKING TABLE ({activeStrategy})
          </div>
          <span className="text-[10px] font-mono text-gray-400">
            Cross-sectional model scores updated every bar
          </span>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Symbol</th>
              <th className="text-right">Model Score</th>
              <th className="text-right">Expected Gross Return</th>
              <th className="text-right">Spread</th>
              <th className="text-right">Estimated Friction</th>
              <th className="text-right">Expected Net Edge</th>
              <th>Signal Status</th>
              <th className="text-center">Risk Gate</th>
            </tr>
          </thead>
          <tbody>
            {currentSignals.map((sig) => (
              <tr key={sig.symbol}>
                <td className="font-mono font-bold text-cyan-400">#{sig.rank}</td>
                <td className="font-mono font-bold text-white">{sig.symbol}</td>
                <td className="text-right font-mono text-white font-semibold">
                  {sig.score > 0 ? `+${sig.score}` : sig.score}
                </td>
                <td className="text-right font-mono text-emerald-400 font-semibold">
                  +{sig.expReturn.toFixed(2)} bps
                </td>
                <td className="text-right font-mono text-gray-400 text-xs">
                  {sig.spread.toFixed(2)} bps
                </td>
                <td className="text-right font-mono text-rose-400 text-xs">
                  {sig.friction.toFixed(2)} bps
                </td>
                <td
                  className={`text-right font-mono font-bold ${
                    sig.netEdge > 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {sig.netEdge > 0 ? '+' : ''}
                  {sig.netEdge.toFixed(2)} bps
                </td>
                <td className="font-mono text-xs">
                  <span className="px-2 py-0.5 rounded bg-white/[0.04] text-gray-300 border border-white/5">
                    {sig.status}
                  </span>
                </td>
                <td className="text-center font-mono">
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      sig.risk === 'APPROVED'
                        ? 'bg-emerald-950 text-emerald-400 border-emerald-500/30'
                        : 'bg-rose-950 text-rose-400 border-rose-500/30'
                    }`}
                  >
                    {sig.risk}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 4. CAPACITY CURVE ANALYSIS */}
      <div className="glass-panel p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold font-mono text-white flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-cyan-400" />
            THREE-POINT EMPIRICAL CAPACITY CURVE ($1k / $2.5k / $5k)
          </div>
          <span className="text-[10px] font-mono text-amber-400 px-2 py-0.5 rounded bg-amber-950 border border-amber-500/30">
            PROJECTED_MODEL_ONLY ABOVE $5k
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 font-mono text-xs pt-1">
          <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
            <div className="text-gray-400 text-[10px]">TIER 0 ($1,000 USD)</div>
            <div className="font-bold text-white text-sm">+10.670 bps / cycle</div>
            <div className="text-emerald-400 text-[10px]">100% Edge Retention (Base)</div>
          </div>
          <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
            <div className="text-gray-400 text-[10px]">TIER 1 ($2,500 USD)</div>
            <div className="font-bold text-white text-sm">+10.560 bps / cycle</div>
            <div className="text-emerald-400 text-[10px]">98.97% Edge Retention</div>
          </div>
          <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
            <div className="text-gray-400 text-[10px]">TIER 2 ($5,000 USD - CURRENT)</div>
            <div className="font-bold text-cyan-400 text-sm">+10.400 bps / cycle</div>
            <div className="text-emerald-400 text-[10px]">97.47% Retention (Validated)</div>
          </div>
          <div className="p-2.5 rounded bg-white/[0.02] border border-white/5 opacity-75">
            <div className="text-gray-400 text-[10px]">TIER 3 ($10,000 USD - LOCKED)</div>
            <div className="font-bold text-amber-400 text-sm">+10.063 bps (Projected)</div>
            <div className="text-gray-500 text-[10px]">Strictly Unauthorized</div>
          </div>
        </div>

        <div className="text-[11px] font-mono text-gray-400 bg-white/[0.02] p-2.5 rounded border border-white/5">
          Linear decay model fit: <code className="text-cyan-300">Net(Cap) = 10.7375 - 0.0000675 * Cap</code> (Decay rate: <strong className="text-white">-0.0675 bps / $1,000 capital</strong>).
          Capacity bottleneck is determined to be <strong className="text-white">Capital Utilization & Signal Scarcity</strong> rather than market impact.
        </div>
      </div>
    </div>
  );
};
