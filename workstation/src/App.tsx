import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, ScreenTab } from './components/Sidebar';
import { DashboardScreen } from './screens/DashboardScreen';
import { MarketsScreen } from './screens/MarketsScreen';
import { PortfolioScreen } from './screens/PortfolioScreen';
import { StrategiesScreen } from './screens/StrategiesScreen';
import { TradesScreen } from './screens/TradesScreen';
import { RiskScreen } from './screens/RiskScreen';
import { AICopilotScreen } from './screens/AICopilotScreen';
import { SystemAuditScreen } from './screens/SystemAuditScreen';
import { api } from './api';
import {
  AccountSummary,
  MarketQuote,
  PortfolioExposure,
  PortfolioRiskTelemetry,
  PositionItem,
  StrategyCard,
  SystemStatusTelemetry,
  TradeRecord,
} from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<ScreenTab>('dashboard');
  const [account, setAccount] = useState<AccountSummary | null>(null);
  const [strategies, setStrategies] = useState<StrategyCard[]>([]);
  const [positions, setPositions] = useState<PositionItem[]>([]);
  const [trades, setTrades] = useState<TradeRecord[]>([]);
  const [watchlist, setWatchlist] = useState<MarketQuote[]>([]);
  const [exposure, setExposure] = useState<PortfolioExposure | null>(null);
  const [risk, setRisk] = useState<PortfolioRiskTelemetry | null>(null);
  const [system, setSystem] = useState<SystemStatusTelemetry | null>(null);

  const refreshAll = async () => {
    try {
      const [acc, strats, pos, trds, wl, exp, rsk, sys] = await Promise.all([
        api.getAccount().catch(() => null),
        api.getStrategies().catch(() => []),
        api.getPositions().catch(() => []),
        api.getTrades().catch(() => []),
        api.getWatchlist().catch(() => []),
        api.getPortfolioExposure().catch(() => null),
        api.getRisk().catch(() => null),
        api.getSystemStatus().catch(() => null),
      ]);

      if (acc) setAccount(acc);
      if (strats.length) setStrategies(strats);
      if (pos.length) setPositions(pos);
      if (trds.length) setTrades(trds);
      if (wl.length) setWatchlist(wl);
      if (exp) setExposure(exp);
      if (rsk) setRisk(rsk);
      if (sys) setSystem(sys);
    } catch (err) {
      console.error('Workstation fetch error:', err);
    }
  };

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 10000); // 10s telemetry heartbeat
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#080a0f] text-gray-200 flex flex-col font-sans">
      <Header account={account} system={system} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />

        <main className="flex-1 p-5 overflow-y-auto bg-gradient-to-b from-[#080a0f] via-[#0b0e17] to-[#080a0f]">
          {currentTab === 'dashboard' && (
            <DashboardScreen account={account} strategies={strategies} trades={trades} />
          )}
          {currentTab === 'markets' && <MarketsScreen watchlist={watchlist} />}
          {currentTab === 'portfolio' && (
            <PortfolioScreen positions={positions} exposure={exposure} risk={risk} />
          )}
          {currentTab === 'strategies' && <StrategiesScreen strategies={strategies} />}
          {currentTab === 'trades' && <TradesScreen trades={trades} />}
          {currentTab === 'risk' && <RiskScreen risk={risk} />}
          {currentTab === 'copilot' && <AICopilotScreen />}
          {currentTab === 'system' && <SystemAuditScreen system={system} />}
        </main>
      </div>
    </div>
  );
};
