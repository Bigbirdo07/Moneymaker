import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Briefcase,
  Layers,
  ScrollText,
  AlertTriangle,
  Bot,
  Sliders,
  Server,
} from 'lucide-react';

export type ScreenTab =
  | 'dashboard'
  | 'markets'
  | 'portfolio'
  | 'strategies'
  | 'trades'
  | 'risk'
  | 'research'
  | 'copilot'
  | 'system';

interface Props {
  currentTab: ScreenTab;
  onSelectTab: (tab: ScreenTab) => void;
}

export const Sidebar: React.FC<Props> = ({ currentTab, onSelectTab }) => {
  const navItems: Array<{ id: ScreenTab; label: string; icon: React.FC<{ className?: string }> }> = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'markets', label: 'Markets', icon: TrendingUp },
    { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
    { id: 'strategies', label: 'Strategies', icon: Layers },
    { id: 'trades', label: 'Trades', icon: ScrollText },
    { id: 'risk', label: 'Risk', icon: AlertTriangle },
    { id: 'research', label: 'Research Lab', icon: Server },
    { id: 'copilot', label: 'AI Copilot', icon: Bot },
    { id: 'system', label: 'System / Audit', icon: Sliders },
  ];


  return (
    <aside className="w-56 border-r border-white/10 bg-[#090b10] flex flex-col justify-between p-3 shrink-0 select-none">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-mono uppercase text-gray-400 font-bold tracking-wider">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-950/80 to-blue-950/60 text-cyan-400 border border-cyan-500/40 shadow-sm shadow-cyan-500/10'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/[0.03]'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-gray-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Footer System Box */}
      <div className="p-3 rounded bg-white/[0.02] border border-white/5 space-y-1.5 font-mono text-[10px]">
        <div className="flex justify-between items-center text-gray-400">
          <span>PORTFOLIO CAP</span>
          <span className="text-white font-semibold">$15,000 USD</span>
        </div>
        <div className="flex justify-between items-center text-gray-400">
          <span>KILL SWITCH</span>
          <span className="text-emerald-400 font-semibold">ARMED (3/3)</span>
        </div>
        <div className="flex justify-between items-center text-gray-400">
          <span>GIT COMMIT</span>
          <span className="text-gray-300">e23a99c</span>
        </div>
      </div>
    </aside>
  );
};
