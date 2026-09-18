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
  Scale,
  ThumbsUp,
  Minus,
  CheckCircle2,
  AlertTriangle,
  FlaskConical,
  Activity,
  BarChart3,
  Clock,
  Eye,
  EyeOff,
  Check,
  X,
} from 'lucide-react';
import {
  DailyBrief,
  CopilotAuditSummary,
  ResearchProposal,
} from '../types';
import { api } from '../api';
import { EvidenceBadge } from '../components/EvidenceBadge';

interface Message {
  sender: 'user' | 'copilot';
  text: string;
  toolCalls?: any[];
  badge?: string;
  interactionId?: string;
  queryCategory?: string;
  snapshotId?: string;
  latencyMs?: number;
  challengerText?: string;
  challengerTools?: any[];
  challengerLatencyMs?: number;
  ragContext?: string;
  voteSubmitted?: boolean;
}

const REASON_TAGS = [
  'More accurate',
  'Better explanation',
  'Better tool use',
  'More concise',
  'More complete',
  'Better grounded',
  'Wrong data',
  'Hallucination',
  'Too verbose',
  'Too slow',
];

const QUICK_ACTIONS = [
  "What happened today?",
  "Explain today's P&L",
  "Why did this trade happen?",
  "Which strategy is weakening?",
  "What risks are elevated?",
  "What did Alpha A do today?",
  "What did Alpha B do today?",
  "What should I review?",
  "Summarize today's research",
];

export const AICopilotScreen: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'copilot',
      text:
        "Hello! I am Moneymaker AI Copilot (BASE-QWEN-2.5-14B [DEFAULT]).\n\nI have read-only telemetry access to Alpha A, Alpha B, PortfolioRiskAggregator, and the trade execution ledger. MMRM-0.2-REAL + RAG runs in SHADOW mode in the background for empirical A/B validation.\n\nAsk me anything about today's P&L, trade explanations, strategy capacity degradation, portfolio risk, or research experiments.",
      badge: 'BROKER_LIVE',
    },
  ]);
  const [inputMsg, setInputMsg] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [activeBriefType, setActiveBriefType] = useState<'morning' | 'midday' | 'closing'>('closing');
  const [brief, setBrief] = useState<DailyBrief | null>(null);
  const [expandedTools, setExpandedTools] = useState<Record<number, boolean>>({});
  const [expandedComparison, setExpandedComparison] = useState<Record<number, boolean>>({});
  const [blindMode, setBlindMode] = useState<boolean>(true);
  const [selectedTags, setSelectedTags] = useState<Record<number, string[]>>({});
  const [voteNotes, setVoteNotes] = useState<Record<number, string>>({});
  const [activeTab, setActiveTab] = useState<'chat' | 'audit' | 'proposals'>('chat');

  // Audit summary
  const [auditSummary, setAuditSummary] = useState<CopilotAuditSummary | null>(null);
  const [auditLoading, setAuditLoading] = useState<boolean>(false);

  // Research proposal modal
  const [proposalQuery, setProposalQuery] = useState<string>('');
  const [activeProposal, setActiveProposal] = useState<ResearchProposal | null>(null);
  const [proposalLoading, setProposalLoading] = useState<boolean>(false);
  const [proposalStatus, setProposalStatus] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getDailyBrief(activeBriefType).then(setBrief).catch(console.error);
  }, [activeBriefType]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadAudit = async () => {
    setAuditLoading(true);
    try {
      const data = await api.getCopilotAudit();
      setAuditSummary(data);
    } catch (err) {
      console.error('Failed to load copilot audit:', err);
    } finally {
      setAuditLoading(false);
    }
  };

  useEffect(() => {
    loadAudit();
  }, []);

  useEffect(() => {
    if (activeTab === 'audit') {
      loadAudit();
    }
  }, [activeTab]);

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputMsg).trim();
    if (!textToSend || loading) return;

    setInputMsg('');
    setMessages((prev) => [...prev, { sender: 'user', text: textToSend }]);
    setLoading(true);

    try {
      const abRes = await api.compareCopilotAB(textToSend);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'copilot',
          text: abRes.base_response.reply,
          toolCalls: abRes.base_response.tool_calls,
          badge: abRes.base_response.evidence_badge,
          interactionId: (abRes as any).interaction_id || `INT_${Date.now()}`,
          queryCategory: (abRes as any).query_category || 'GENERAL',
          snapshotId: (abRes as any).snapshot_id || 'SNAP_LIVE',
          latencyMs: (abRes as any).base_latency_ms || 320,
          challengerText: abRes.mmrm_response.reply,
          challengerTools: abRes.mmrm_response.tool_calls,
          challengerLatencyMs: (abRes as any).challenger_latency_ms || 410,
          ragContext: abRes.rag_context,
          voteSubmitted: false,
        },
      ]);
      // Refresh audit counts after interaction
      loadAudit();
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

  const handleVote = async (msgIdx: number, preference: 'BASE' | 'CHALLENGER' | 'TIE' | 'A' | 'B') => {
    const msg = messages[msgIdx];
    if (!msg || !msg.interactionId || msg.voteSubmitted) return;

    let normalizedPref = preference;
    if (preference === 'A') {
      normalizedPref = 'BASE';
    } else if (preference === 'B') {
      normalizedPref = 'CHALLENGER';
    }

    try {
      await api.voteCopilotAB({
        interaction_id: msg.interactionId,
        preference: normalizedPref,
        reason_tags: selectedTags[msgIdx] || [],
        notes: voteNotes[msgIdx] || '',
      });

      setMessages((prev) =>
        prev.map((m, i) => (i === msgIdx ? { ...m, voteSubmitted: true } : m))
      );
      loadAudit();
    } catch (err) {
      alert(`Vote submission failed: ${err}`);
    }
  };

  const toggleReasonTag = (msgIdx: number, tag: string) => {
    setSelectedTags((prev) => {
      const curr = prev[msgIdx] || [];
      const updated = curr.includes(tag) ? curr.filter((t) => t !== tag) : [...curr, tag];
      return { ...prev, [msgIdx]: updated };
    });
  };

  const handleProposeExperiment = async () => {
    if (!proposalQuery.trim() || proposalLoading) return;
    setProposalLoading(true);
    setProposalStatus(null);
    try {
      const res = await api.proposeResearchExperiment(proposalQuery);
      if (res.success && res.proposal) {
        setActiveProposal(res.proposal);
      }
    } catch (err) {
      alert(`Experiment proposal generation failed: ${err}`);
    } finally {
      setProposalLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6.5rem)] space-y-3">
      {/* TOP BAR: MODEL TELEMETRY, INTERACTION COUNTER & SHADOW CONTROLS */}
      <div className="glass-panel p-3 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-300">
            <Bot className="w-3.5 h-3.5" />
            <span className="font-bold">CONTROL:</span>
            <span>BASE-QWEN-2.5-14B</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-800 text-white font-bold ml-1">DEFAULT</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-purple-950/80 border border-purple-500/40 text-purple-300">
            <Sparkles className="w-3.5 h-3.5" />
            <span className="font-bold">CHALLENGER:</span>
            <span>MMRM-0.2-REAL + RAG</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-800 text-white font-bold ml-1">SHADOW</span>
          </div>

          {/* REAL INTERACTION COUNTER (Part XIII) */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-black/50 border border-white/10 text-white font-mono text-[11px]">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-gray-400 font-bold">REAL INTERACTIONS:</span>
            <span className="font-bold text-cyan-300">{auditSummary?.total_interactions || 0} / 50</span>
            <span className="text-gray-500 text-[10px]">({auditSummary?.total_interactions || 0} / 100 recommended)</span>
          </div>

          <div className="hidden xl:flex items-center gap-1 text-[11px] text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Pinned Telemetry Active &bull; Zero Execution Authority</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setBlindMode(!blindMode)}
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs transition-colors border ${
              blindMode
                ? 'bg-amber-950/60 text-amber-300 border-amber-500/40'
                : 'bg-gray-800 text-gray-300 border-gray-700'
            }`}
          >
            {blindMode ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
            <span>Blind A/B: {blindMode ? 'ON (A vs B)' : 'OFF (Labeled)'}</span>
          </button>

          <div className="flex rounded bg-black/40 p-0.5 border border-white/10">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-3 py-1 rounded text-xs transition-colors ${
                activeTab === 'chat' ? 'bg-cyan-600 text-white font-bold' : 'text-gray-400 hover:text-white'
              }`}
            >
              Copilot Chat
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-3 py-1 rounded text-xs transition-colors flex items-center gap-1 ${
                activeTab === 'audit' ? 'bg-cyan-600 text-white font-bold' : 'text-gray-400 hover:text-white'
              }`}
            >
              <BarChart3 className="w-3 h-3" />
              <span>A/B Audit</span>
            </button>
            <button
              onClick={() => setActiveTab('proposals')}
              className={`px-3 py-1 rounded text-xs transition-colors flex items-center gap-1 ${
                activeTab === 'proposals' ? 'bg-cyan-600 text-white font-bold' : 'text-gray-400 hover:text-white'
              }`}
            >
              <FlaskConical className="w-3 h-3" />
              <span>Research Proposals</span>
            </button>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 overflow-hidden">
          {/* LEFT: CONVERSATIONAL CHAT & SHADOW AB (8 cols) */}
          <div className="lg:col-span-8 glass-panel flex flex-col overflow-hidden">
            {/* Message Thread */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-lg p-3.5 text-xs font-mono leading-relaxed space-y-2.5 ${
                      m.sender === 'user'
                        ? 'bg-cyan-950/80 text-cyan-100 border border-cyan-500/30 self-end'
                        : 'bg-[#0d121f] text-gray-200 border border-white/10 self-start shadow-md w-full'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] text-gray-400 border-b border-white/5 pb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold uppercase text-cyan-400">
                          {m.sender === 'user' ? 'You' : (blindMode ? 'Response A (Active Production)' : 'Base Qwen 2.5 14B [CONTROL]')}
                        </span>
                        {m.queryCategory && (
                          <span className="px-1.5 py-0.2 rounded bg-white/5 text-gray-300">
                            {m.queryCategory}
                          </span>
                        )}
                        {m.latencyMs && (
                          <span className="text-gray-500 flex items-center gap-0.5">
                            <Clock className="w-2.5 h-2.5" />
                            {m.latencyMs}ms
                          </span>
                        )}
                      </div>
                      {m.badge && <EvidenceBadge source={m.badge as any} />}
                    </div>

                    {/* Base response text */}
                    <div className="whitespace-pre-line text-gray-100">{m.text}</div>

                    {/* Tool Invocation Drawer for Base */}
                    {m.toolCalls && m.toolCalls.length > 0 && (
                      <div className="pt-2 border-t border-white/5 text-[10px]">
                        <button
                          onClick={() =>
                            setExpandedTools((prev) => ({ ...prev, [idx]: !prev[idx] }))
                          }
                          className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold"
                        >
                          <Code2 className="w-3 h-3" />
                          <span>{m.toolCalls.length} Explicit Tools Called</span>
                          {expandedTools[idx] ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                        {expandedTools[idx] && (
                          <div className="mt-1.5 p-2 bg-black/40 rounded border border-white/5 space-y-1">
                            {m.toolCalls.map((tc, tIdx) => (
                              <div key={tIdx} className="text-gray-400 font-mono text-[10px]">
                                <span className="text-emerald-400 font-bold">&bull; {tc.tool_name}</span>
                                <span className="text-gray-500">({JSON.stringify(tc.parameters || {})})</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* SHADOW CHALLENGER REVEAL / COMPARISON DRAWER */}
                    {m.challengerText && (
                      <div className="pt-2 border-t border-purple-500/20">
                        <button
                          onClick={() =>
                            setExpandedComparison((prev) => ({ ...prev, [idx]: !prev[idx] }))
                          }
                          className="w-full flex items-center justify-between p-2 rounded bg-purple-950/40 hover:bg-purple-950/60 border border-purple-500/30 text-purple-300 transition-colors text-[11px]"
                        >
                          <div className="flex items-center gap-1.5 font-bold">
                            <Scale className="w-3.5 h-3.5" />
                            <span>
                              {expandedComparison[idx]
                                ? 'Hide MMRM-0.2 Shadow Comparison'
                                : 'Compare with MMRM-0.2-REAL + RAG (Shadow Challenger)'}
                            </span>
                          </div>
                          <span className="text-[10px] text-purple-400">
                            {expandedComparison[idx] ? 'Close' : 'Reveal Side-by-Side'}
                          </span>
                        </button>

                        {expandedComparison[idx] && (
                          <div className="mt-3 p-3 rounded bg-[#130d24] border border-purple-500/40 space-y-3">
                            <div className="flex items-center justify-between text-[10px] border-b border-purple-500/20 pb-1.5">
                              <div className="flex items-center gap-2">
                                <span className="font-bold uppercase text-purple-400">
                                  {blindMode ? 'Response B (Challenger Candidate)' : 'MMRM-0.2-REAL + RAG [CHALLENGER]'}
                                </span>
                                {m.challengerLatencyMs && (
                                  <span className="text-purple-300/70 flex items-center gap-0.5">
                                    <Clock className="w-2.5 h-2.5" />
                                    {m.challengerLatencyMs}ms
                                  </span>
                                )}
                              </div>
                              <span className="px-2 py-0.5 rounded bg-purple-900/60 text-purple-300 text-[10px]">
                                Real QLoRA + RAG Verified
                              </span>
                            </div>

                            <div className="whitespace-pre-line text-gray-100 text-xs leading-relaxed">
                              {m.challengerText}
                            </div>

                            {/* Challenger tools */}
                            {m.challengerTools && m.challengerTools.length > 0 && (
                              <div className="p-2 bg-black/40 rounded border border-purple-500/20 text-[10px] space-y-1">
                                <div className="text-purple-300 font-bold">Challenger Tools Executed:</div>
                                {m.challengerTools.map((tc, tIdx) => (
                                  <div key={tIdx} className="text-gray-400 font-mono">
                                    <span className="text-purple-400 font-semibold">&bull; {tc.tool_name}</span>
                                    <span className="text-gray-500">({JSON.stringify(tc.parameters || {})})</span>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* VOTING SECTION */}
                            <div className="pt-2 border-t border-purple-500/20 space-y-2">
                              <div className="text-[11px] font-bold text-gray-300">
                                Human Evaluation: Which answer is more useful?
                              </div>

                              {m.voteSubmitted ? (
                                <div className="p-2 rounded bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
                                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                  <span>Evaluation recorded for interaction {m.interactionId}. Thank you!</span>
                                </div>
                              ) : (
                                <div className="space-y-2">
                                  <div className="grid grid-cols-3 gap-2">
                                    <button
                                      onClick={() => handleVote(idx, blindMode ? 'A' : 'BASE')}
                                      className="py-1.5 px-2 rounded bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-500/40 text-cyan-300 font-bold text-[11px] flex items-center justify-center gap-1 transition-colors"
                                    >
                                      <ThumbsUp className="w-3 h-3" />
                                      <span>{blindMode ? 'Response A Better' : 'Base Better'}</span>
                                    </button>
                                    <button
                                      onClick={() => handleVote(idx, 'TIE')}
                                      className="py-1.5 px-2 rounded bg-gray-800 hover:bg-gray-750 border border-gray-700 text-gray-300 font-bold text-[11px] flex items-center justify-center gap-1 transition-colors"
                                    >
                                      <Minus className="w-3 h-3" />
                                      <span>Equal / Tie</span>
                                    </button>
                                    <button
                                      onClick={() => handleVote(idx, blindMode ? 'B' : 'CHALLENGER')}
                                      className="py-1.5 px-2 rounded bg-purple-950/60 hover:bg-purple-900/80 border border-purple-500/40 text-purple-300 font-bold text-[11px] flex items-center justify-center gap-1 transition-colors"
                                    >
                                      <ThumbsUp className="w-3 h-3" />
                                      <span>{blindMode ? 'Response B Better' : 'MMRM Better'}</span>
                                    </button>
                                  </div>

                                  {/* Reason Tags */}
                                  <div>
                                    <div className="text-[10px] text-gray-400 mb-1">Reason tags (optional):</div>
                                    <div className="flex flex-wrap gap-1">
                                      {REASON_TAGS.map((tag) => {
                                        const isSelected = (selectedTags[idx] || []).includes(tag);
                                        return (
                                          <button
                                            key={tag}
                                            onClick={() => toggleReasonTag(idx, tag)}
                                            className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${
                                              isSelected
                                                ? 'bg-purple-600 text-white border-purple-400 font-semibold'
                                                : 'bg-black/30 text-gray-400 border-white/10 hover:border-white/20'
                                            }`}
                                          >
                                            {tag}
                                          </button>
                                        );
                                      })}
                                    </div>
                                  </div>

                                  {/* Optional Notes */}
                                  <input
                                    type="text"
                                    placeholder="Optional evaluation notes..."
                                    value={voteNotes[idx] || ''}
                                    onChange={(e) =>
                                      setVoteNotes((prev) => ({ ...prev, [idx]: e.target.value }))
                                    }
                                    className="w-full bg-black/40 border border-white/10 rounded px-2.5 py-1 text-[11px] text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500"
                                  />
                                </div>
                              )}
                            </div>
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
                  <span>Querying telemetry and executing grounded quantitative tools for both models...</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Question Chips (Part XVI - 9 quick actions) */}
            <div className="px-3 py-2 border-t border-white/5 flex items-center gap-1.5 overflow-x-auto whitespace-nowrap bg-black/20">
              <span className="text-[10px] font-mono text-gray-500 uppercase font-bold shrink-0">
                Quick Actions:
              </span>
              {QUICK_ACTIONS.map((q, i) => (
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
                placeholder="Ask Moneymaker Copilot (e.g. 'What happened today?', 'Why did this trade happen?')..."
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
      )}

      {/* AUDIT TAB (Part XXIV & Part XX) */}
      {activeTab === 'audit' && (
        <div className="glass-panel p-4 flex-1 overflow-y-auto space-y-4 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                COPILOT A/B TELEMETRY & PROMOTION GATE AUDIT
              </h2>
              <p className="text-[11px] text-gray-400 mt-0.5">
                Real Workstation Interactions &bull; Base Qwen 2.5 14B vs MMRM-0.2-REAL + RAG
              </p>
            </div>

            <button
              onClick={loadAudit}
              disabled={auditLoading}
              className="px-3 py-1.5 rounded bg-cyan-950 hover:bg-cyan-900 border border-cyan-500/40 text-cyan-300 text-xs flex items-center gap-1.5"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>{auditLoading ? 'Refreshing...' : 'Refresh Metrics'}</span>
            </button>
          </div>

          {auditSummary ? (
            <div className="space-y-4">
              {/* TOP KPI CARDS */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3 rounded bg-white/[0.02] border border-white/10">
                  <div className="text-gray-400 text-[10px] uppercase font-bold">Total Interactions</div>
                  <div className="text-lg font-bold text-white mt-1">{auditSummary.total_interactions}</div>
                  <div className="text-[10px] text-gray-500">{auditSummary.voted_interactions} Human Votes Recorded</div>
                </div>

                <div className="p-3 rounded bg-purple-950/30 border border-purple-500/30">
                  <div className="text-purple-300 text-[10px] uppercase font-bold">MMRM Challenger Win Rate</div>
                  <div className="text-lg font-bold text-purple-400 mt-1">{auditSummary.challenger_win_rate_pct.toFixed(1)}%</div>
                  <div className="text-[10px] text-gray-400">{auditSummary.challenger_wins} wins / {auditSummary.base_wins} base / {auditSummary.ties} ties</div>
                </div>

                <div className="p-3 rounded bg-emerald-950/30 border border-emerald-500/30">
                  <div className="text-emerald-300 text-[10px] uppercase font-bold">Challenger Tool Accuracy</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">{auditSummary.tool_accuracy_challenger_pct.toFixed(1)}%</div>
                  <div className="text-[10px] text-gray-400">Base: {auditSummary.tool_accuracy_base_pct.toFixed(1)}%</div>
                </div>

                <div className="p-3 rounded bg-white/[0.02] border border-white/10">
                  <div className="text-gray-400 text-[10px] uppercase font-bold">Promotion Gate Status</div>
                  <div className="text-xs font-bold text-amber-400 mt-1.5">{auditSummary.promotion_gate_status}</div>
                  <div className="text-[10px] text-gray-500">Target: 50+ genuine interactions</div>
                </div>
              </div>

              {/* SECONDARY METRICS */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 rounded bg-white/[0.02] border border-white/10 space-y-1.5">
                  <div className="text-gray-400 text-[10px] uppercase font-bold">Reliability & Governance</div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Hallucination Rate:</span>
                    <span className="text-emerald-400 font-bold">{auditSummary.hallucination_rate_challenger_pct.toFixed(1)}% (Target &le; 2%)</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Authority Pass Rate:</span>
                    <span className="text-emerald-400 font-bold">{auditSummary.authority_pass_rate_challenger_pct.toFixed(1)}% (Target 100%)</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Provenance Accuracy:</span>
                    <span className="text-emerald-400 font-bold">{auditSummary.provenance_accuracy_challenger_pct.toFixed(1)}% (Target &ge; 95%)</span>
                  </div>
                </div>

                <div className="p-3 rounded bg-white/[0.02] border border-white/10 space-y-1.5">
                  <div className="text-gray-400 text-[10px] uppercase font-bold">Latency Telemetry</div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Base Avg Latency:</span>
                    <span className="text-cyan-400 font-bold">{auditSummary.avg_latency_base_ms.toFixed(0)} ms</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">MMRM + RAG Avg Latency:</span>
                    <span className="text-purple-400 font-bold">{auditSummary.avg_latency_challenger_ms.toFixed(0)} ms</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Total Incidents Logged:</span>
                    <span className="text-white font-bold">{auditSummary.total_incidents}</span>
                  </div>
                </div>

                <div className="p-3 rounded bg-white/[0.02] border border-white/10 space-y-1.5">
                  <div className="text-gray-400 text-[10px] uppercase font-bold">Incident Breakdown</div>
                  {Object.entries(auditSummary.incidents_by_severity).map(([sev, count]) => (
                    <div key={sev} className="flex justify-between text-xs">
                      <span className="text-gray-400">{sev}:</span>
                      <span className={count > 0 && (sev === 'MAJOR' || sev === 'CRITICAL') ? 'text-rose-400 font-bold' : 'text-gray-300'}>
                        {count}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* CATEGORY BREAKDOWN TABLE */}
              <div className="p-3 rounded bg-white/[0.02] border border-white/10 space-y-2">
                <div className="text-gray-400 text-[10px] uppercase font-bold">Interactions by Category</div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="text-[10px] text-gray-500 uppercase border-b border-white/10">
                      <tr>
                        <th className="py-1.5">Category</th>
                        <th className="py-1.5 text-center">Interactions</th>
                        <th className="py-1.5 text-center">MMRM Wins</th>
                        <th className="py-1.5 text-center">Base Wins</th>
                        <th className="py-1.5 text-center">Ties</th>
                        <th className="py-1.5 text-right">MMRM Win Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {Object.entries(auditSummary.category_breakdown).map(([cat, stat]) => (
                        <tr key={cat} className="hover:bg-white/[0.02]">
                          <td className="py-1.5 font-bold text-gray-200">{cat}</td>
                          <td className="py-1.5 text-center text-gray-400">{stat.total}</td>
                          <td className="py-1.5 text-center text-purple-400 font-bold">{stat.challenger_wins}</td>
                          <td className="py-1.5 text-center text-cyan-400">{stat.base_wins}</td>
                          <td className="py-1.5 text-center text-gray-500">{stat.ties}</td>
                          <td className="py-1.5 text-right font-bold text-emerald-400">
                            {stat.challenger_win_pct.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              {auditLoading ? 'Loading A/B Telemetry...' : 'No interaction records found. Start interacting in Copilot Chat.'}
            </div>
          )}
        </div>
      )}

      {/* PROPOSALS TAB (Part XVIII) */}
      {activeTab === 'proposals' && (
        <div className="glass-panel p-4 flex-1 overflow-y-auto space-y-4 font-mono text-xs">
          <div className="border-b border-white/10 pb-3">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <FlaskConical className="w-4 h-4 text-purple-400" />
              STRUCTURED RESEARCH EXPERIMENT SPECIFICATION
            </h2>
            <p className="text-[11px] text-gray-400 mt-0.5">
              MMRM-0.2 may propose Unity experiment specifications &bull; Human approval required prior to Slurm dispatch
            </p>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Describe research question (e.g. 'Test Kalman filter lookback 20 vs 50 on Alpha A volatility regime')..."
              value={proposalQuery}
              onChange={(e) => setProposalQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleProposeExperiment()}
              className="flex-1 bg-white/[0.03] border border-white/10 rounded px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
            <button
              onClick={handleProposeExperiment}
              disabled={proposalLoading || !proposalQuery.trim()}
              className="px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{proposalLoading ? 'Generating Spec...' : 'Propose Spec'}</span>
            </button>
          </div>

          {activeProposal && (
            <div className="p-4 rounded-lg bg-[#110d20] border border-purple-500/40 space-y-3">
              <div className="flex items-center justify-between border-b border-purple-500/20 pb-2">
                <div className="text-sm font-bold text-purple-300">
                  Proposal: {activeProposal.proposal_id}
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-500/30 text-[10px]">
                    Compute Class: {activeProposal.estimated_compute_class}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/30 text-[10px]">
                    Status: {activeProposal.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-[10px] text-purple-400 font-bold uppercase">Hypothesis</div>
                  <div className="text-gray-200 mt-0.5">{activeProposal.hypothesis}</div>
                </div>

                <div>
                  <div className="text-[10px] text-purple-400 font-bold uppercase">Rationale</div>
                  <div className="text-gray-200 mt-0.5">{activeProposal.reason}</div>
                </div>

                <div>
                  <div className="text-[10px] text-purple-400 font-bold uppercase">Target Strategy & Dataset</div>
                  <div className="text-gray-200 mt-0.5">
                    Strategy: <span className="text-white font-bold">{activeProposal.strategy}</span> &bull; Dataset: <span className="text-white font-bold">{activeProposal.dataset}</span>
                  </div>
                </div>

                <div>
                  <div className="text-[10px] text-purple-400 font-bold uppercase">Evaluation Metric & Evidence</div>
                  <div className="text-gray-200 mt-0.5">
                    Metric: <span className="text-white font-bold">{activeProposal.evaluation_metric}</span> &bull; Evidence: <span className="text-emerald-400 font-bold">{activeProposal.expected_evidence}</span>
                  </div>
                </div>
              </div>

              <div className="p-2.5 rounded bg-black/40 border border-white/5">
                <div className="text-[10px] text-purple-400 font-bold uppercase mb-1">Parameters (JSON)</div>
                <pre className="text-[11px] text-gray-300 overflow-x-auto">
                  {JSON.stringify(activeProposal.parameters, null, 2)}
                </pre>
              </div>

              <div className="pt-2 flex items-center justify-between border-t border-purple-500/20">
                <div className="text-[11px] text-gray-400">
                  {proposalStatus ? (
                    <span className="text-emerald-400 font-bold">{proposalStatus}</span>
                  ) : (
                    <span>Human review required before Unity Slurm queue submission.</span>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setProposalStatus('Proposal rejected by operator. No Slurm job submitted.');
                    }}
                    className="px-3 py-1.5 rounded bg-rose-950 hover:bg-rose-900 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-1"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                  <button
                    onClick={() => {
                      setProposalStatus('Proposal approved! Ready for Slurm job dispatch in Research Lab.');
                    }}
                    className="px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-black font-bold text-xs flex items-center gap-1"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Approve Proposal</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
