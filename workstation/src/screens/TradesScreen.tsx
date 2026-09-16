import React, { useState } from 'react';
import {
  ScrollText,
  HelpCircle,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  ExternalLink,
  ShieldCheck,
  X,
} from 'lucide-react';
import { TradeRecord, TradeExplanation } from '../types';
import { api } from '../api';
import { EvidenceBadge } from '../components/EvidenceBadge';

interface Props {
  trades: TradeRecord[];
}

export const TradesScreen: React.FC<Props> = ({ trades }) => {
  const [selectedExplanation, setSelectedExplanation] = useState<TradeExplanation | null>(null);
  const [loadingExplainer, setLoadingExplainer] = useState<boolean>(false);
  const [filterStrategy, setFilterStrategy] = useState<string>('ALL');

  const handleExplain = async (tradeId: string) => {
    setLoadingExplainer(true);
    try {
      const exp = await api.explainTrade(tradeId);
      setSelectedExplanation(exp);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingExplainer(false);
    }
  };

  const filteredTrades = trades.filter((t) => {
    if (filterStrategy === 'ALL') return true;
    return t.strategy.includes(filterStrategy);
  });

  return (
    <div className="space-y-6">
      {/* 1. HEADER & FILTER BAR */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div>
          <div className="text-sm font-bold font-mono text-white flex items-center gap-2">
            <ScrollText className="w-4 h-4 text-cyan-400" />
            COMPREHENSIVE TRADE JOURNAL ({trades.length} Verified Executions)
          </div>
          <div className="text-xs text-gray-400 font-mono">
            Every trade is strictly backed by live broker execution orders and deterministic risk decisions.
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-gray-400">Filter Strategy:</span>
          {(['ALL', 'ALPHA_A', 'ALPHA_B'] as const).map((strat) => (
            <button
              key={strat}
              onClick={() => setFilterStrategy(strat)}
              className={`px-2.5 py-1 rounded border ${
                filterStrategy === strat
                  ? 'bg-cyan-950 text-cyan-400 border-cyan-500/40 font-bold'
                  : 'text-gray-400 hover:text-white border-white/5 bg-white/[0.02]'
              }`}
            >
              {strat}
            </button>
          ))}
          <EvidenceBadge source="BROKER_LIVE" />
        </div>
      </div>

      {/* 2. TRADES JOURNAL TABLE */}
      <div className="glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Trade ID</th>
                <th>Strategy</th>
                <th>Symbol</th>
                <th>Broker Order ID</th>
                <th>Entry Time</th>
                <th>Exit Time</th>
                <th className="text-right">Shares</th>
                <th className="text-right">Entry</th>
                <th className="text-right">Exit</th>
                <th className="text-right">Gross P&L</th>
                <th className="text-right">Cost</th>
                <th className="text-right">Net P&L</th>
                <th className="text-right">Return</th>
                <th className="text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredTrades.map((t) => {
                const isAlphaA = t.strategy.includes('ALPHA_A');
                const isPnlPositive = t.net_pnl >= 0;
                return (
                  <tr key={t.trade_id}>
                    <td className="font-mono font-bold text-white text-xs">{t.trade_id}</td>
                    <td>
                      <span
                        className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${
                          isAlphaA
                            ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/30'
                            : 'bg-blue-950/80 text-blue-300 border-blue-500/30'
                        }`}
                      >
                        {isAlphaA ? 'ALPHA A' : 'ALPHA B'}
                      </span>
                    </td>
                    <td className="font-mono font-bold text-white">{t.symbol}</td>
                    <td className="font-mono text-[11px] text-gray-400">{t.broker_order_id}</td>
                    <td className="font-mono text-gray-400 text-xs">
                      {new Date(t.entry_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="font-mono text-gray-400 text-xs">
                      {t.exit_timestamp
                        ? new Date(t.exit_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        : 'OPEN'}
                    </td>
                    <td className="text-right font-mono text-white">{t.shares}</td>
                    <td className="text-right font-mono text-gray-300">${t.entry_price.toFixed(2)}</td>
                    <td className="text-right font-mono text-gray-300">
                      {t.exit_price ? `$${t.exit_price.toFixed(2)}` : '—'}
                    </td>
                    <td className="text-right font-mono text-gray-300">
                      ${t.gross_pnl.toFixed(2)}
                    </td>
                    <td className="text-right font-mono text-rose-400 text-xs">
                      ${t.canonical_cost.toFixed(2)}
                    </td>
                    <td
                      className={`text-right font-mono font-bold ${
                        isPnlPositive ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {isPnlPositive ? '+' : ''}${t.net_pnl.toFixed(2)}
                    </td>
                    <td
                      className={`text-right font-mono font-bold ${
                        isPnlPositive ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {isPnlPositive ? '+' : ''}{t.return_pct.toFixed(2)}%
                    </td>
                    <td className="text-center">
                      <button
                        onClick={() => handleExplain(t.trade_id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-900 text-xs font-mono font-semibold transition-colors shadow-sm"
                      >
                        <HelpCircle className="w-3 h-3 text-cyan-400" />
                        <span>WHY?</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. TRADE EXPLANATION MODAL / DRAWER */}
      {selectedExplanation && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel max-w-2xl w-full border border-cyan-500/30 p-6 space-y-5 relative shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div>
                <div className="text-base font-bold font-mono text-white flex items-center gap-2">
                  <Zap className="w-4 h-4 text-cyan-400" />
                  Grounded Trade Explanation: {selectedExplanation.symbol} ({selectedExplanation.trade_id})
                </div>
                <div className="text-xs font-mono text-gray-400">
                  Strategy: {selectedExplanation.strategy}
                </div>
              </div>
              <button
                onClick={() => setSelectedExplanation(null)}
                className="p-1 rounded text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Explanation Sections */}
            <div className="space-y-3 font-mono text-xs text-gray-300">
              <div className="p-3 rounded bg-white/[0.02] border border-white/5">
                <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                  1. SIGNAL GENERATION
                </div>
                <div className="text-white mt-1">{selectedExplanation.signal_summary}</div>
              </div>

              <div className="p-3 rounded bg-white/[0.02] border border-white/5">
                <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                  2. WHY THIS ASSET WAS SELECTED
                </div>
                <div className="text-white mt-1">{selectedExplanation.why_selected}</div>
              </div>

              <div className="p-3 rounded bg-white/[0.02] border border-white/5">
                <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                  3. EXPECTED EDGE (CANONICAL ACCOUNTING)
                </div>
                <div className="text-emerald-400 mt-1 font-semibold">
                  {selectedExplanation.expected_edge}
                </div>
              </div>

              <div className="p-3 rounded bg-white/[0.02] border border-white/5 space-y-1">
                <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                  4. RISK GATE CHECKS PASSED
                </div>
                <ul className="space-y-1 text-gray-200 pl-2">
                  {selectedExplanation.risk_checks.map((rc, idx) => (
                    <li key={idx} className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                      <span>{rc}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded bg-white/[0.02] border border-white/5">
                <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                  5. EXECUTION & RESULT
                </div>
                <div className="text-white mt-1">{selectedExplanation.execution_details}</div>
                <div className="text-emerald-300 font-bold mt-1">
                  {selectedExplanation.current_result}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-white/10 pt-3 text-[11px] font-mono">
              <EvidenceBadge source={selectedExplanation.evidence_provenance} />
              <button
                onClick={() => setSelectedExplanation(null)}
                className="px-4 py-1.5 rounded bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition-colors"
              >
                Close Explanation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
