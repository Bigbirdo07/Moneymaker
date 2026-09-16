import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  Zap,
  HelpCircle,
  FileText,
  ShieldCheck,
  Code2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { CopilotChatResponse, DailyBrief } from '../types';
import { api } from '../api';
import { EvidenceBadge } from '../components/EvidenceBadge';

export const AICopilotScreen: React.FC = () => {
  const [messages, setMessages] = useState<
    Array<{ sender: 'user' | 'copilot'; text: string; toolCalls?: any[]; badge?: string }>
  >([
    {
      sender: 'copilot',
      text:
        "Hello! I am Moneymaker AI Copilot. I have live, read-only telemetry access to the entire platform (Alpha A, Alpha B, PortfolioRiskAggregator, and the trade execution ledger).\n\nAsk me anything about today's P&L, why trades were made, strategy capacity degradation, or portfolio risk simulation.",
      badge: 'BROKER_LIVE',
    },
  ]);
  const [inputMsg, setInputMsg] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [activeBriefType, setActiveBriefType] = useState<'morning' | 'midday' | 'closing'>('closing');
  const [brief, setBrief] = useState<DailyBrief | null>(null);
  const [showTools, setShowTools] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    'What happened today?',
    'Why did we buy AMD?',
    'Why didn\'t we buy NVDA?',
    'Is either strategy degrading?',
    'How much risk do we have right now?',
    'What happens if the market drops 5%?',
    'What positions are open?',
  ];

  useEffect(() => {
    api.getDailyBrief(activeBriefType).then(setBrief).catch(console.error);
  }, [activeBriefType]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputMsg).trim();
    if (!textToSend || loading) return;

    setInputMsg('');
    setMessages((prev) => [...prev, { sender: 'user', text: textToSend }]);
    setLoading(true);

    try {
      const res: CopilotChatResponse = await api.chatCopilot(textToSend);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: res.reply,
          toolCalls: res.tool_calls,
          badge: res.evidence_badge,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: 'Error communicating with Moneymaker Copilot service.',
          badge: 'PROJECTED',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-6.5rem)]">
      {/* LEFT: CONVERSATIONAL CHAT (8 cols) */}
      <div className="lg:col-span-8 glass-panel flex flex-col overflow-hidden">
        {/* Chat Header */}
        <div className="p-3.5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="text-xs font-bold font-mono text-white flex items-center gap-2">
                MONEYMAKER COPILOT (READ-ONLY)
                <EvidenceBadge source="BROKER_LIVE" />
              </div>
              <div className="text-[10px] text-gray-400 font-mono">
                Tool-Grounded Quantitative Research Assistant &bull; Zero Direct Broker Authority
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30">
              23 Tools Active
            </span>
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-xl rounded-lg p-3.5 text-xs font-mono leading-relaxed space-y-2 ${
                  m.sender === 'user'
                    ? 'bg-cyan-950/80 text-cyan-100 border border-cyan-500/30 self-end'
                    : 'bg-[#0d121f] text-gray-200 border border-white/10 self-start shadow-md'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-gray-400 border-b border-white/5 pb-1 mb-1">
                  <span className="font-bold uppercase text-cyan-400">
                    {m.sender === 'user' ? 'You' : 'Moneymaker AI Copilot'}
                  </span>
                  {m.badge && <EvidenceBadge source={m.badge} />}
                </div>

                <div className="whitespace-pre-line">{m.text}</div>

                {/* Tool Invocation Drawer */}
                {m.toolCalls && m.toolCalls.length > 0 && (
                  <div className="pt-2 border-t border-white/5 text-[10px]">
                    <button
                      onClick={() => setShowTools(!showTools)}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold"
                    >
                      <Code2 className="w-3 h-3" />
                      <span>{m.toolCalls.length} Explicit Tools Called</span>
                      {showTools ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </button>
                    {showTools && (
                      <div className="mt-1.5 p-2 bg-black/40 rounded border border-white/5 space-y-1">
                        {m.toolCalls.map((tc, tIdx) => (
                          <div key={tIdx} className="text-gray-400">
                            <span className="text-emerald-400 font-bold">&bull; {tc.tool_name}()</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 p-2">
              <Sparkles className="w-4 h-4 animate-spin" />
              <span>Querying telemetry and executing grounded quantitative tools...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Question Chips */}
        <div className="px-4 py-2 border-t border-white/5 flex items-center gap-1.5 overflow-x-auto whitespace-nowrap bg-black/20">
          <span className="text-[10px] font-mono text-gray-500 uppercase font-bold shrink-0">
            Suggested:
          </span>
          {suggestedQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q)}
              className="text-[11px] font-mono px-2.5 py-1 rounded bg-white/[0.03] hover:bg-cyan-950/60 text-gray-300 hover:text-cyan-300 border border-white/5 hover:border-cyan-500/30 transition-all shrink-0"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-white/10 bg-[#090b10] flex items-center gap-2">
          <input
            type="text"
            placeholder="Ask Moneymaker Copilot (e.g. 'Why did we buy AMD?', 'What happened today?')..."
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            className="flex-1 bg-white/[0.03] border border-white/10 rounded px-3 py-2 text-xs font-mono text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !inputMsg.trim()}
            className="px-4 py-2 rounded bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-bold text-xs font-mono flex items-center gap-1.5 transition-colors"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send</span>
          </button>
        </div>
      </div>

      {/* RIGHT: DAILY AI BRIEFS (4 cols) */}
      <div className="lg:col-span-4 glass-panel flex flex-col overflow-hidden">
        <div className="p-3.5 border-b border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold font-mono text-white flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              STRUCTURED DAILY AI BRIEFS
            </div>
            <EvidenceBadge source="BROKER_LIVE" />
          </div>

          <div className="grid grid-cols-3 gap-1 font-mono text-xs">
            {(['morning', 'midday', 'closing'] as const).map((b) => (
              <button
                key={b}
                onClick={() => setActiveBriefType(b)}
                className={`py-1 text-center rounded uppercase font-bold text-[10px] border transition-all ${
                  activeBriefType === b
                    ? 'bg-cyan-950 text-cyan-400 border-cyan-500/40'
                    : 'text-gray-400 border-white/5 bg-white/[0.02]'
                }`}
              >
                {b}
              </button>
            ))}
          </div>
        </div>

        {brief ? (
          <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
            <div>
              <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                1. EXECUTIVE HIGHLIGHTS
              </div>
              <ul className="mt-1 space-y-1 text-gray-200 pl-2">
                {brief.summary_bullets.map((bullet, i) => (
                  <li key={i} className="leading-snug">
                    &bull; {bullet}
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-2.5 rounded bg-white/[0.02] border border-white/5">
              <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                2. P&L REALIZATION
              </div>
              <div className="text-emerald-400 font-bold mt-0.5">{brief.pnl_summary}</div>
            </div>

            <div className="space-y-1">
              <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                3. STRATEGY ACTIVITY
              </div>
              {Object.entries(brief.strategy_activity).map(([strat, act], i) => (
                <div key={i} className="p-2 rounded bg-white/[0.02] border border-white/5">
                  <div className="text-white font-semibold">{strat}:</div>
                  <div className="text-gray-400 text-[11px]">{act}</div>
                </div>
              ))}
            </div>

            <div className="space-y-1">
              <div className="text-gray-400 text-[10px] uppercase font-bold text-cyan-400">
                4. RISK & UPCOMING EVENTS
              </div>
              <div className="text-gray-300 space-y-0.5 pl-2">
                {brief.risk_and_alerts.map((ra, i) => (
                  <div key={i} className="text-amber-300">&bull; {ra}</div>
                ))}
                {brief.upcoming_events.map((ue, i) => (
                  <div key={i} className="text-gray-400">&bull; {ue}</div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 text-xs font-mono text-gray-500">Loading brief telemetry...</div>
        )}
      </div>
    </div>
  );
};
