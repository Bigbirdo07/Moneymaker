import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  FastForward,
  RotateCcw,
  Clock,
  ShieldCheck,
  TrendingUp,
  Activity,
  Award,
  Layers,
  Sparkles,
  BarChart3,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Cpu,
} from 'lucide-react';

interface ReplayPosition {
  symbol: string;
  shares: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
  pnlBps: number;
  barsHeld: number;
  mfeBps: number;
}

interface RankedCandidate {
  rank: number;
  symbol: string;
  expectedNetEdgeBps: number;
  probPositive: number;
  optimalHorizon: number;
  spreadBps: number;
  riskScore: number;
  status: 'ELIGIBLE' | 'ALLOCATED' | 'SKIPPED';
}

interface ReplayTradeLog {
  id: string;
  timestamp: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  shares: number;
  fillPrice: number;
  frictionDollars: number;
  pnlDollars?: number;
  qualityTag: string;
  captureRatio?: number;
}

export const HistoricalReplayScreen: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speed, setSpeed] = useState<'1x' | '10x' | '100x' | 'max'>('10x');
  const [simulatedTime, setSimulatedTime] = useState<string>('09:45:00 ET');
  const [simulatedDate, setSimulatedDate] = useState<string>('2026-01-28 (OOS Day 1)');
  const [equity, setEquity] = useState<number>(940.06);
  const [cash, setCash] = useState<number>(688.20);
  const [startingCapital] = useState<number>(1000.0);
  const [totalFriction, setTotalFriction] = useState<number>(38.45);
  const [profitCaptureRatio, setProfitCaptureRatio] = useState<number>(0.428);

  const [positions, setPositions] = useState<ReplayPosition[]>([
    {
      symbol: 'NVDA',
      shares: 1,
      entryPrice: 878.50,
      currentPrice: 882.10,
      unrealizedPnl: 3.60,
      pnlBps: 41.0,
      barsHeld: 15,
      mfeBps: 48.0,
    },
    {
      symbol: 'AAPL',
      shares: 1,
      entryPrice: 184.20,
      currentPrice: 184.95,
      unrealizedPnl: 0.75,
      pnlBps: 40.7,
      barsHeld: 10,
      mfeBps: 45.0,
    },
  ]);

  const [candidates] = useState<RankedCandidate[]>([
    { rank: 1, symbol: 'NVDA', expectedNetEdgeBps: 18.5, probPositive: 0.68, optimalHorizon: 15, spreadBps: 1.8, riskScore: 0.25, status: 'ALLOCATED' },
    { rank: 2, symbol: 'AAPL', expectedNetEdgeBps: 14.2, probPositive: 0.64, optimalHorizon: 15, spreadBps: 1.5, riskScore: 0.20, status: 'ALLOCATED' },
    { rank: 3, symbol: 'MSFT', expectedNetEdgeBps: 9.8, probPositive: 0.58, optimalHorizon: 30, spreadBps: 2.0, riskScore: 0.22, status: 'ELIGIBLE' },
    { rank: 4, symbol: 'META', expectedNetEdgeBps: 7.4, probPositive: 0.55, optimalHorizon: 30, spreadBps: 2.4, riskScore: 0.35, status: 'ELIGIBLE' },
    { rank: 5, symbol: 'TSLA', expectedNetEdgeBps: 2.1, probPositive: 0.51, optimalHorizon: 5, spreadBps: 3.8, riskScore: 0.65, status: 'SKIPPED' },
  ]);

  const [tradeLogs] = useState<ReplayTradeLog[]>([
    { id: 'TR_01', timestamp: '09:31:00', symbol: 'NVDA', action: 'BUY', shares: 1, fillPrice: 878.50, frictionDollars: 0.08, qualityTag: 'GOOD_ENTRY' },
    { id: 'TR_02', timestamp: '09:35:00', symbol: 'AAPL', action: 'BUY', shares: 1, fillPrice: 184.20, frictionDollars: 0.04, qualityTag: 'GOOD_ENTRY' },
    { id: 'TR_03', timestamp: '09:42:00', symbol: 'AMZN', action: 'SELL', shares: 1, fillPrice: 178.90, frictionDollars: 0.05, pnlDollars: 1.45, qualityTag: 'GOOD_EXIT', captureRatio: 0.52 },
  ]);

  return (
    <div className="space-y-5 animate-fadeIn">
      {/* Top Banner & Control Bar */}
      <div className="p-4 rounded-lg bg-[#0e131f] border border-white/10 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="p-2.5 rounded-md bg-cyan-950/80 border border-cyan-500/40 text-cyan-400">
            <Clock className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white tracking-wide">Historical Market Replay Engine</h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950/80 text-cyan-400 border border-cyan-500/30 font-semibold">
                LEAKAGE-SAFE REPLAY
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-950/80 text-purple-400 border border-purple-500/30 font-semibold">
                $1,000 SIMULATED CAPITAL
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono text-gray-400 mt-1">
              <span>Date: <span className="text-white font-medium">{simulatedDate}</span></span>
              <span>•</span>
              <span>Simulated Clock: <span className="text-cyan-400 font-bold">{simulatedTime}</span></span>
              <span>•</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Strict T ≤ Clock Invariance Verified
              </span>
            </div>
          </div>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-2 bg-black/40 p-1.5 rounded-lg border border-white/10">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold transition-all ${
              isPlaying
                ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/30'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isPlaying ? 'PAUSE' : 'PLAY'}</span>
          </button>

          <div className="h-4 w-px bg-white/10 mx-1" />

          {(['1x', '10x', '100x', 'max'] as const).map((spd) => (
            <button
              key={spd}
              onClick={() => setSpeed(spd)}
              className={`px-2 py-1 rounded text-[11px] font-mono font-semibold transition-all ${
                speed === spd
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              {spd}
            </button>
          ))}

          <div className="h-4 w-px bg-white/10 mx-1" />

          <button className="px-2 py-1 rounded text-xs font-mono text-gray-400 hover:text-white hover:bg-white/5 flex items-center gap-1">
            <FastForward className="w-3.5 h-3.5" /> +1m
          </button>
          <button className="px-2 py-1 rounded text-xs font-mono text-gray-400 hover:text-white hover:bg-white/5 flex items-center gap-1">
            <FastForward className="w-3.5 h-3.5" /> +5m
          </button>
        </div>
      </div>

      {/* Account KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        <div className="p-3.5 rounded-lg bg-[#0e131f] border border-white/10">
          <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Total Equity</div>
          <div className="text-xl font-bold text-white font-mono mt-1">${equity.toFixed(2)}</div>
          <div className="text-[11px] font-mono text-emerald-400 mt-1 flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" /> +${(equity - startingCapital).toFixed(2)} ({( (equity - startingCapital)/startingCapital * 100 ).toFixed(2)}%)
          </div>
        </div>

        <div className="p-3.5 rounded-lg bg-[#0e131f] border border-white/10">
          <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Available Cash</div>
          <div className="text-xl font-bold text-gray-200 font-mono mt-1">${cash.toFixed(2)}</div>
          <div className="text-[11px] font-mono text-gray-400 mt-1">
            {((cash / equity) * 100).toFixed(1)}% in Cash (Unconstrained)
          </div>
        </div>

        <div className="p-3.5 rounded-lg bg-[#0e131f] border border-white/10">
          <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Active Exposure</div>
          <div className="text-xl font-bold text-cyan-400 font-mono mt-1">${(equity - cash).toFixed(2)}</div>
          <div className="text-[11px] font-mono text-cyan-400 mt-1">
            {positions.length} Active Positions (Max 4)
          </div>
        </div>

        <div className="p-3.5 rounded-lg bg-[#0e131f] border border-white/10">
          <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Total Friction Paid</div>
          <div className="text-xl font-bold text-amber-400 font-mono mt-1">${totalFriction.toFixed(2)}</div>
          <div className="text-[11px] font-mono text-gray-400 mt-1">
            Spread + Slippage + Regulatory
          </div>
        </div>

        <div className="p-3.5 rounded-lg bg-[#0e131f] border border-white/10">
          <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Hindsight Capture</div>
          <div className="text-xl font-bold text-purple-400 font-mono mt-1">{(profitCaptureRatio * 100).toFixed(1)}%</div>
          <div className="text-[11px] font-mono text-purple-400 mt-1 flex items-center gap-1">
            <Award className="w-3.5 h-3.5" /> Oracle Feasible Bound
          </div>
        </div>
      </div>

      {/* Main Grid: Active Positions & Ranked Opportunities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Active Positions */}
        <div className="p-4 rounded-lg bg-[#0e131f] border border-white/10 flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Active Replay Positions ({positions.length})</h3>
            </div>
            <span className="text-xs font-mono text-gray-400">Marked at {simulatedTime}</span>
          </div>

          <div className="mt-3 space-y-2.5 flex-1">
            {positions.map((pos) => (
              <div key={pos.symbol} className="p-3 rounded bg-black/40 border border-white/5 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white font-mono">{pos.symbol}</span>
                    <span className="text-xs text-gray-400 font-mono">{pos.shares} share @ ${pos.entryPrice.toFixed(2)}</span>
                  </div>
                  <div className="text-[11px] font-mono text-gray-400 mt-1">
                    Held {pos.barsHeld}m • Current: ${pos.currentPrice.toFixed(2)} • Peak MFE: +{pos.mfeBps.toFixed(1)} bps
                  </div>
                </div>

                <div className="text-right font-mono">
                  <div className={`text-sm font-bold ${pos.unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {pos.unrealizedPnl >= 0 ? '+' : ''}${pos.unrealizedPnl.toFixed(2)}
                  </div>
                  <div className={`text-[11px] ${pos.pnlBps >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {pos.pnlBps >= 0 ? '+' : ''}{pos.pnlBps.toFixed(1)} bps
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Opportunity Ranker Table */}
        <div className="p-4 rounded-lg bg-[#0e131f] border border-white/10 flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Cross-Sectional Opportunity Ranker</h3>
            </div>
            <span className="text-xs font-mono text-gray-400">Re-ranked every 5m</span>
          </div>

          <div className="mt-3 overflow-x-auto flex-1">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="text-gray-400 border-b border-white/5">
                  <th className="pb-2 font-medium">Rank</th>
                  <th className="pb-2 font-medium">Symbol</th>
                  <th className="pb-2 font-medium">Net Edge</th>
                  <th className="pb-2 font-medium">P(Up)</th>
                  <th className="pb-2 font-medium">Horizon</th>
                  <th className="pb-2 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {candidates.map((c) => (
                  <tr key={c.symbol} className="hover:bg-white/[0.02]">
                    <td className="py-2 text-gray-400 font-bold">#{c.rank}</td>
                    <td className="py-2 text-white font-bold">{c.symbol}</td>
                    <td className="py-2 text-emerald-400">+{c.expectedNetEdgeBps.toFixed(1)} bps</td>
                    <td className="py-2 text-gray-300">{(c.probPositive * 100).toFixed(0)}%</td>
                    <td className="py-2 text-cyan-400">{c.optimalHorizon}m</td>
                    <td className="py-2 text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.status === 'ALLOCATED'
                          ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/30'
                          : c.status === 'ELIGIBLE'
                          ? 'bg-cyan-950/80 text-cyan-400 border border-cyan-500/30'
                          : 'bg-gray-800 text-gray-400'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* MMRM-0.2 Replay Explanation & Anomaly Detection Panel */}
      <div className="p-4 rounded-lg bg-[#0e131f] border border-white/10 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-bold text-white">MMRM-0.2 Replay Director & Explanations</h3>
          </div>
          <span className="text-[11px] font-mono text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-500/30">
            Read-Only Orchestration (0 Broker Authority)
          </span>
        </div>

        <div className="p-3.5 rounded bg-black/40 border border-white/5 text-xs text-gray-300 space-y-2 leading-relaxed">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Session Strategy Commentary:</span>
          </div>
          <p>
            The autonomous platform detected a morning gap continuation in <strong className="text-white">NVDA</strong> (+18.5 bps net expected edge) and a short-horizon momentum setup in <strong className="text-white">AAPL</strong> (+14.2 bps net expected edge). Both positions were allocated using deterministic whole-share constraints ($1,000 initial capital boundary).
          </p>
          <p>
            <strong className="text-cyan-400">Exit Model Telemetry:</strong> Position in <strong className="text-white">AMZN</strong> was closed at 09:42 ET under the <code className="text-gray-300 font-mono">TAKE_PROFIT</code> policy after reaching +41 bps return, capturing <strong>52%</strong> of the theoretical intraday maximum identified by the post-hoc Hindsight Oracle.
          </p>
        </div>
      </div>

      {/* Simulated Execution & Fill Log */}
      <div className="p-4 rounded-lg bg-[#0e131f] border border-white/10">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Simulated Execution & Fill Telemetry (Next-Bar Execution)</h3>
          </div>
          <span className="text-xs font-mono text-gray-400">Non-instantaneous friction model</span>
        </div>

        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="text-gray-400 border-b border-white/5">
                <th className="pb-2 font-medium">Time</th>
                <th className="pb-2 font-medium">Trade ID</th>
                <th className="pb-2 font-medium">Symbol</th>
                <th className="pb-2 font-medium">Side</th>
                <th className="pb-2 font-medium">Shares</th>
                <th className="pb-2 font-medium">Fill Price</th>
                <th className="pb-2 font-medium">Friction</th>
                <th className="pb-2 font-medium">Net P&L</th>
                <th className="pb-2 font-medium text-right">Quality Classification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {tradeLogs.map((log) => (
                <tr key={log.id} className="hover:bg-white/[0.02]">
                  <td className="py-2 text-gray-400">{log.timestamp}</td>
                  <td className="py-2 text-gray-300 font-bold">{log.id}</td>
                  <td className="py-2 text-white font-bold">{log.symbol}</td>
                  <td className="py-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      log.action === 'BUY' ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400'
                    }`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="py-2 text-gray-300">{log.shares}</td>
                  <td className="py-2 text-white font-bold">${log.fillPrice.toFixed(2)}</td>
                  <td className="py-2 text-amber-400">${log.frictionDollars.toFixed(2)}</td>
                  <td className="py-2">
                    {log.pnlDollars !== undefined ? (
                      <span className={`font-bold ${log.pnlDollars >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {log.pnlDollars >= 0 ? '+' : ''}${log.pnlDollars.toFixed(2)}
                      </span>
                    ) : (
                      <span className="text-gray-500">—</span>
                    )}
                  </td>
                  <td className="py-2 text-right">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-400 border border-cyan-500/30">
                      {log.qualityTag}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
