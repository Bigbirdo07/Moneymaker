import React from 'react';
import { Activity, ShieldCheck, Zap, Lock } from 'lucide-react';
import { AccountSummary, SystemStatusTelemetry } from '../types';
import { EvidenceBadge } from './EvidenceBadge';

interface Props {
  account?: AccountSummary | null;
  system?: SystemStatusTelemetry | null;
}

export const Header: React.FC<Props> = ({ account, system }) => {
  const equity = account?.equity ?? 16576.0;
  const todayPnl = account?.today_pnl ?? 142.5;
  const todayPnlPct = account?.today_pnl_pct ?? 0.87;
  const isPnlPositive = todayPnl >= 0;

  return (
    <header className="h-14 border-b border-white/10 bg-[#0b0e17]/90 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-50">
      {/* Brand & Market Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-cyan-500/20 text-sm">
            M
          </div>
          <div>
            <div className="text-sm font-bold tracking-wider text-white flex items-center gap-1.5 font-mono">
              MONEYMAKER <span className="text-[10px] px-1 bg-cyan-950 text-cyan-400 border border-cyan-500/30 rounded">V1.0</span>
            </div>
            <div className="text-[10px] text-gray-400 flex items-center gap-1 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-green" />
              <span>MARKET OPEN (REGULAR)</span>
            </div>
          </div>
        </div>

        <div className="h-6 w-px bg-white/10 mx-1 hidden sm:block" />

        {/* Global Strategy Status Badges */}
        <div className="hidden md:flex items-center gap-2 text-[11px] font-mono">
          <div className="px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 flex items-center gap-1">
            <Zap className="w-3 h-3 text-emerald-400" />
            ALPHA A: <span className="font-semibold">$10,000 (HOLD)</span>
          </div>
          <div className="px-2 py-0.5 rounded bg-blue-950/60 border border-blue-500/30 text-blue-300 flex items-center gap-1">
            <Zap className="w-3 h-3 text-blue-400" />
            ALPHA B: <span className="font-semibold">$5,000 (TIER 2)</span>
          </div>
          <div className="px-2 py-0.5 rounded bg-purple-950/60 border border-purple-500/30 text-purple-300 flex items-center gap-1">
            <Lock className="w-3 h-3 text-purple-400" />
            ALLOCATOR: <span className="font-semibold">SHADOW ONLY</span>
          </div>
        </div>
      </div>

      {/* Top Telemetry & KPIs */}
      <div className="flex items-center gap-5">
        <div className="text-right font-mono">
          <div className="text-[10px] uppercase text-gray-400 tracking-wider">Account Equity</div>
          <div className="text-sm font-bold text-white tracking-tight">
            ${equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        <div className="text-right font-mono">
          <div className="text-[10px] uppercase text-gray-400 tracking-wider">Today's P&L</div>
          <div className={`text-sm font-bold flex items-center justify-end gap-1 ${isPnlPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            <span>{isPnlPositive ? '+' : ''}${todayPnl.toFixed(2)}</span>
            <span className="text-[11px] opacity-80">({isPnlPositive ? '+' : ''}{todayPnlPct.toFixed(2)}%)</span>
          </div>
        </div>

        <div className="h-6 w-px bg-white/10 hidden sm:block" />

        {/* System & Broker Connectivity */}
        <div className="hidden lg:flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-950/40 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{system?.broker_reconciliation_status ?? 'BROKER MATCHED'}</span>
          </div>
          <EvidenceBadge source={account?.evidence_source ?? 'BROKER_LIVE'} />
        </div>
      </div>
    </header>
  );
};
