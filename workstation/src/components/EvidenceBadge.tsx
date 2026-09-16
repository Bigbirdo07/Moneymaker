import React from 'react';
import { EvidenceSource } from '../types';

interface Props {
  source: EvidenceSource | string;
  size?: 'sm' | 'md';
}

export const EvidenceBadge: React.FC<Props> = ({ source, size = 'sm' }) => {
  const getStyle = (src: string) => {
    switch (src) {
      case 'BROKER_LIVE':
      case 'LIVE':
      case 'VERIFIED_LIVE':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40';
      case 'BROKER_PAPER':
      case 'PAPER':
        return 'bg-blue-950/80 text-blue-400 border-blue-500/40';
      case 'FORWARD_SHADOW':
      case 'SHADOW':
        return 'bg-purple-950/80 text-purple-400 border-purple-500/40';
      case 'HISTORICAL':
        return 'bg-amber-950/80 text-amber-400 border-amber-500/40';
      case 'SIMULATED':
        return 'bg-orange-950/80 text-orange-400 border-orange-500/40';
      case 'PROJECTED':
        return 'bg-rose-950/80 text-rose-400 border-rose-500/40';
      default:
        return 'bg-gray-900 text-gray-400 border-gray-700';
    }
  };

  const pad = size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono font-semibold uppercase tracking-wider rounded border ${pad} ${getStyle(
        source
      )}`}
      title={`Evidence Provenance: ${source}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {source.replace('BROKER_', '')}
    </span>
  );
};
