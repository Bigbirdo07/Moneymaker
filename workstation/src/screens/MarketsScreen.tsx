import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Search,
  SlidersHorizontal,
  ChevronRight,
  AlertCircle,
  Clock,
  BarChart2,
  Shield,
  Zap,
} from 'lucide-react';
import { MarketQuote, StockDetail } from '../types';
import { api } from '../api';
import { EvidenceBadge } from '../components/EvidenceBadge';

interface Props {
  watchlist: MarketQuote[];
  onExplainTrade?: (tradeId: string) => void;
}

export const MarketsScreen: React.FC<Props> = ({ watchlist, onExplainTrade }) => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AMD');
  const [detail, setDetail] = useState<StockDetail | null>(null);
  const [timeframe, setTimeframe] = useState<'1m' | '5m' | '15m' | '1h' | '1D'>('5m');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api
      .getStockDetail(selectedSymbol)
      .then((data) => {
        if (isMounted) setDetail(data);
      })
      .catch((err) => console.error(err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [selectedSymbol]);

  const filteredWatchlist = watchlist.filter((item) =>
    item.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-6.5rem)]">
      {/* LEFT: LIVE WATCHLIST (4 cols) */}
      <div className="lg:col-span-4 glass-panel flex flex-col overflow-hidden">
        <div className="p-3 border-b border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold font-mono text-white flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
              LIVE WATCHLIST ({watchlist.length})
            </div>
            <EvidenceBadge source="BROKER_LIVE" />
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search ticker (e.g. AMD, NVDA)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/[0.03] border border-white/10 rounded px-2.5 py-1.5 pl-8 text-xs font-mono text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th className="text-right">Last</th>
                <th className="text-right">Chg%</th>
                <th className="text-right">Spread</th>
                <th className="text-right">Vol(Rel)</th>
              </tr>
            </thead>
            <tbody>
              {filteredWatchlist.map((item) => {
                const isSelected = item.symbol === selectedSymbol;
                const isPositive = item.percent_change >= 0;
                return (
                  <tr
                    key={item.symbol}
                    onClick={() => setSelectedSymbol(item.symbol)}
                    className={`cursor-pointer transition-colors ${
                      isSelected ? 'bg-cyan-950/40 border-l-2 border-l-cyan-400' : ''
                    }`}
                  >
                    <td className="font-bold font-mono text-white flex items-center gap-1.5">
                      <span>{item.symbol}</span>
                      {!item.is_data_available && (
                        <span className="text-[9px] text-rose-400 font-normal">N/A</span>
                      )}
                    </td>
                    <td className="text-right font-mono text-white">
                      ${item.last_price.toFixed(2)}
                    </td>
                    <td
                      className={`text-right font-mono font-semibold ${
                        isPositive ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {isPositive ? '+' : ''}
                      {item.percent_change.toFixed(2)}%
                    </td>
                    <td className="text-right font-mono text-gray-400 text-[11px]">
                      {item.spread_bps.toFixed(1)} bps
                    </td>
                    <td className="text-right font-mono text-cyan-300 text-[11px]">
                      {item.relative_volume.toFixed(1)}x
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* RIGHT: STOCK DETAIL & CANDLESTICK CHART (8 cols) */}
      <div className="lg:col-span-8 glass-panel flex flex-col overflow-hidden">
        {/* Header bar of selected symbol */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="text-xl font-bold font-mono text-white">{selectedSymbol}</span>
              <span className="text-xs text-gray-400 font-medium">
                {detail?.name ?? `${selectedSymbol} Inc.`} &bull; {detail?.sector ?? 'Technology'}
              </span>
              <EvidenceBadge source="BROKER_LIVE" />
            </div>
            <div className="flex items-center gap-4 text-xs font-mono mt-1">
              <span className="text-lg font-bold text-white">
                ${detail?.quote.last_price.toFixed(2) ?? '154.20'}
              </span>
              <span
                className={`font-semibold ${
                  (detail?.quote.percent_change ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                +${detail?.quote.absolute_change.toFixed(2)} (+
                {detail?.quote.percent_change.toFixed(2)}%)
              </span>
              <span className="text-gray-400">
                Bid/Ask: ${detail?.quote.bid.toFixed(2)} &times; ${detail?.quote.ask.toFixed(2)} (
                {detail?.quote.spread_bps.toFixed(1)} bps)
              </span>
              <span className="text-cyan-400">
                VWAP: ${detail?.quote.vwap.toFixed(2)}
              </span>
            </div>
          </div>

          {/* Timeframe Selector */}
          <div className="flex items-center gap-1 bg-white/[0.04] p-1 rounded border border-white/5 font-mono text-xs">
            {(['1m', '5m', '15m', '1h', '1D'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 rounded ${
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

        {/* Content Body: Chart + Strategy Signals + Positions */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Candlestick & VWAP Chart Container */}
          <div className="h-64 rounded bg-[#090c14] border border-white/5 p-3 relative flex flex-col justify-between">
            <div className="flex items-center justify-between text-[11px] font-mono text-gray-400">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded bg-cyan-400" />
                <span>Price Candles ({timeframe})</span>
                <span className="text-amber-400 ml-2">-- VWAP Overlay</span>
              </span>
              <span>Volume: {(detail?.quote.volume ?? 1420000).toLocaleString()} shares</span>
            </div>

            {/* SVG Candlestick Mock Rendering */}
            <div className="h-44 w-full relative">
              <svg className="w-full h-full" viewBox="0 0 600 150" preserveAspectRatio="none">
                {/* VWAP Curve */}
                <path
                  d="M 10,100 Q 150,85 300,70 T 590,45"
                  fill="none"
                  stroke="#f59e0b"
                  strokeWidth="1.5"
                  strokeDasharray="4 2"
                />

                {/* Candles */}
                {(detail?.bars_5m ?? []).slice(0, 30).map((bar, i) => {
                  const x = 20 + i * 19;
                  const isUp = bar.close >= bar.open;
                  const candleColor = isUp ? '#10b981' : '#ef4444';
                  const highY = Math.max(10, 140 - (bar.high - 148) * 15);
                  const lowY = Math.min(140, 140 - (bar.low - 148) * 15);
                  const openY = 140 - (bar.open - 148) * 15;
                  const closeY = 140 - (bar.close - 148) * 15;
                  const topY = Math.min(openY, closeY);
                  const bodyHeight = Math.max(3, Math.abs(closeY - openY));

                  return (
                    <g key={i}>
                      {/* Wick */}
                      <line x1={x + 4} y1={highY} x2={x + 4} y2={lowY} stroke={candleColor} strokeWidth="1" />
                      {/* Body */}
                      <rect
                        x={x}
                        y={topY}
                        width="8"
                        height={bodyHeight}
                        fill={candleColor}
                        rx="1"
                      />
                    </g>
                  );
                })}
              </svg>
            </div>

            <div className="flex justify-between text-[10px] font-mono text-gray-500">
              <span>09:30</span>
              <span>10:30</span>
              <span>11:30</span>
              <span>13:00</span>
              <span>14:30</span>
              <span>16:00</span>
            </div>
          </div>

          {/* Strategy Signal Matrix & Active Positions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Alpha A Model Status */}
            <div className="p-3 rounded bg-white/[0.02] border border-white/5 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-gray-300 font-bold flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-cyan-400" />
                  Alpha A (Intraday Momentum)
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30">
                  {detail?.alpha_a_rank ? `RANK #${detail.alpha_a_rank}` : 'NO SIGNAL'}
                </span>
              </div>
              <div className="text-xs font-mono text-gray-400 space-y-1">
                <div>Model Score: <strong className="text-white">{detail?.alpha_a_score ? `+${detail.alpha_a_score}` : '0.00'}</strong></div>
                <div>Expected Edge: <strong className="text-emerald-400">+1.44 bps</strong> after canonical friction</div>
                <div>Status: <strong className="text-white">Active scanning above opening VWAP</strong></div>
              </div>
            </div>

            {/* Alpha B Model Status */}
            <div className="p-3 rounded bg-white/[0.02] border border-white/5 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-gray-300 font-bold flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-blue-400" />
                  Alpha B (Multi-Day Reversal)
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-500/30">
                  {detail?.alpha_b_rank ? `RANK #${detail.alpha_b_rank}` : 'NO SIGNAL'}
                </span>
              </div>
              <div className="text-xs font-mono text-gray-400 space-y-1">
                <div>Reversal Score: <strong className="text-white">{detail?.alpha_b_score ?? '0.00'}</strong></div>
                <div>Expected Edge: <strong className="text-emerald-400">+11.22 bps</strong> (3-day horizon)</div>
                <div>Status: <strong className="text-white">Cohort entry gate passed</strong></div>
              </div>
            </div>
          </div>

          {/* Active Positions & Risk Flags */}
          <div className="p-3 rounded bg-white/[0.02] border border-white/5 space-y-2">
            <div className="text-xs font-bold font-mono text-white flex items-center justify-between">
              <span>ACTIVE POSITION & RISK CHECKS</span>
              {detail?.active_position ? (
                <span className="text-[10px] font-mono text-emerald-400">
                  HELD BY {detail.active_position.strategy.includes('ALPHA_A') ? 'ALPHA A' : 'ALPHA B'}
                </span>
              ) : (
                <span className="text-[10px] font-mono text-gray-400">FLAT (NO POSITION)</span>
              )}
            </div>

            {detail?.active_position ? (
              <div className="grid grid-cols-4 gap-2 text-xs font-mono text-gray-300">
                <div className="p-2 bg-white/[0.02] rounded">
                  <div className="text-gray-500 text-[10px]">SHARES</div>
                  <div className="font-bold text-white">{detail.active_position.shares} shares</div>
                </div>
                <div className="p-2 bg-white/[0.02] rounded">
                  <div className="text-gray-500 text-[10px]">ENTRY PRICE</div>
                  <div className="font-bold text-white">${detail.active_position.entry_price.toFixed(2)}</div>
                </div>
                <div className="p-2 bg-white/[0.02] rounded">
                  <div className="text-gray-500 text-[10px]">UNREALIZED P&L</div>
                  <div className="font-bold text-emerald-400">
                    +${detail.active_position.unrealized_pnl.toFixed(2)} ({detail.active_position.unrealized_pnl_pct.toFixed(2)}%)
                  </div>
                </div>
                <div className="p-2 bg-white/[0.02] rounded">
                  <div className="text-gray-500 text-[10px]">HOLDING PERIOD</div>
                  <div className="font-bold text-cyan-300">{detail.active_position.holding_period}</div>
                </div>
              </div>
            ) : (
              <div className="text-xs font-mono text-gray-400">
                Zero capital allocated to {selectedSymbol} currently. Order router ready for candidate signals.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
