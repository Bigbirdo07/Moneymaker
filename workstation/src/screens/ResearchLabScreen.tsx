import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Terminal,
  Layers,
  Database,
  Search,
  CheckCircle2,
  AlertCircle,
  Play,
  XCircle,
  FileText,
  Clock,
  Sparkles,
  ShieldAlert,
  Server,
  RefreshCw,
  Award,
  GitCompare,
  ThumbsUp,
  ThumbsDown,
  ShieldCheck,
} from 'lucide-react';
import {
  HpcJob,
  ExperimentRecord,
  ResearchModelRecord,
  DatasetManifest,
  ResearchDocument,
  CopilotABCompareResponse,
  FourWayBenchmarkMatrix,
} from '../types';
import { api } from '../api';

type ResearchSubTab = 'jobs' | 'experiments' | 'models' | 'ab_eval' | 'datasets' | 'memory';

export const ResearchLabScreen: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<ResearchSubTab>('jobs');
  const [jobs, setJobs] = useState<HpcJob[]>([]);
  const [experiments, setExperiments] = useState<ExperimentRecord[]>([]);
  const [models, setModels] = useState<ResearchModelRecord[]>([]);
  const [datasets, setDatasets] = useState<DatasetManifest[]>([]);
  const [memoryDocs, setMemoryDocs] = useState<ResearchDocument[]>([]);
  const [fourWayMatrix, setFourWayMatrix] = useState<FourWayBenchmarkMatrix | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedLogs, setSelectedLogs] = useState<{ jobId: string; logs: string } | null>(null);

  // A/B Comparison State
  const [abPrompt, setAbPrompt] = useState('Why did we buy AMD and how healthy is Alpha A?');
  const [abResult, setAbResult] = useState<CopilotABCompareResponse | null>(null);
  const [abLoading, setAbLoading] = useState(false);
  const [abFeedbackStatus, setAbFeedbackStatus] = useState<string | null>(null);


  // Job Submission Form State
  const [submitTemplate, setSubmitTemplate] = useState('jobs/gpu_training.slurm');
  const [submitExpId, setSubmitExpId] = useState('');
  const [submitTarget, setSubmitTarget] = useState('UNITY_GPU');
  const [submitting, setSubmitting] = useState(false);

  const refreshData = async () => {
    setLoading(true);
    try {
      const [j, e, m, d, mem, fway] = await Promise.all([
        api.getResearchJobs().catch(() => []),
        api.getResearchExperiments().catch(() => []),
        api.getResearchModels().catch(() => []),
        api.getResearchDatasets().catch(() => []),
        api.getResearchMemory(searchQuery).catch(() => []),
        api.get4WayBenchmark().catch(() => null),
      ]);
      setJobs(j);
      setExperiments(e);
      setModels(m);
      setDatasets(d);
      setMemoryDocs(mem);
      if (fway) setFourWayMatrix(fway);
    } catch (err) {
      console.error('Failed to load research data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, [searchQuery]);

  const handleRunAB = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!abPrompt.trim()) return;
    setAbLoading(true);
    setAbFeedbackStatus(null);
    try {
      const res = await api.compareCopilotAB(abPrompt);
      setAbResult(res);
    } catch (err) {
      alert(`A/B evaluation failed: ${err}`);
    } finally {
      setAbLoading(false);
    }
  };

  const handleFeedback = async (winner: string) => {
    if (!abResult) return;
    try {
      await api.submitCopilotFeedback({
        prompt: abResult.prompt,
        winner,
        notes: `Workstation user evaluation: ${winner}`,
      });
      setAbFeedbackStatus(`Feedback recorded: ${winner}`);
    } catch (err) {
      alert(`Feedback submission failed: ${err}`);
    }
  };

  const handleAuditModel = async (modelId: string) => {
    try {
      const audit = await api.auditModelProvenance(modelId);
      alert(`MODEL PROVENANCE AUDIT FOR ${modelId}:\nStatus: ${audit.status}\nVerified: ${audit.verified}\nChecks: ${JSON.stringify(audit.checks, null, 2)}`);
    } catch (err) {
      alert(`Audit failed: ${err}`);
    }
  };

  const handleJobSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.submitResearchJob({
        slurm_template: submitTemplate,
        experiment_id: submitExpId || `EXP_${Date.now()}`,
        compute_target: submitTarget,
      });
      setSubmitExpId('');
      await refreshData();
    } catch (err) {
      alert(`Submission failed: ${err}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    if (!confirm(`Cancel Slurm job ${jobId}?`)) return;
    try {
      await api.cancelResearchJob(jobId);
      await refreshData();
    } catch (err) {
      alert(`Cancel failed: ${err}`);
    }
  };

  const handleViewLogs = async (jobId: string) => {
    try {
      const res = await api.getResearchJobLogs(jobId);
      setSelectedLogs({ jobId, logs: res.logs });
    } catch (err) {
      alert(`Failed to fetch logs: ${err}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. HEADER */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div>
          <div className="text-sm font-bold font-mono text-white flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            UMASS AMHERST UNITY HPC RESEARCH LAB
          </div>
          <div className="text-xs text-gray-400 font-mono">
            Heavy quantitative research, GPU/CPU Slurm orchestration, Moneymaker Research Model (MMRM-0.1), and Institutional Memory.
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>UNITY HPC: CONNECTED</span>
          </div>
          <button
            onClick={refreshData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40 text-xs font-mono font-bold hover:bg-cyan-900 transition-colors"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Cluster</span>
          </button>
        </div>
      </div>

      {/* 2. SUB-TAB NAVIGATION */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: 'jobs', label: 'Unity Slurm Jobs', icon: Terminal, count: jobs.length },
          { id: 'experiments', label: 'Experiment Registry', icon: Layers, count: experiments.length },
          { id: 'models', label: 'Model Registry & Benchmark', icon: Award, count: models.length },
          { id: 'ab_eval', label: 'A/B Model Evaluator', icon: GitCompare, count: 2 },
          { id: 'datasets', label: 'Dataset Manifests', icon: Database, count: datasets.length },
          { id: 'memory', label: 'Research Memory (RAG)', icon: Search, count: memoryDocs.length },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id as ResearchSubTab)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono font-medium transition-all ${
                isActive
                  ? 'bg-cyan-950/80 text-cyan-400 border border-cyan-500/40 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/[0.03]'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              <span className="px-1.5 py-0.2 rounded bg-black/40 text-[10px] text-gray-300 font-bold">
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>


      {/* 3. SUBTAB CONTENT */}

      {/* A. UNITY SLURM JOBS */}
      {activeSubTab === 'jobs' && (
        <div className="space-y-4">
          {/* Submit New Job Panel */}
          <div className="glass-panel p-4 space-y-3">
            <div className="text-xs font-bold font-mono text-white flex items-center gap-2">
              <Play className="w-3.5 h-3.5 text-cyan-400" />
              SUBMIT OFFLINE RESEARCH JOB TO UNITY SLURM
            </div>
            <form onSubmit={handleJobSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div>
                <label className="text-[10px] font-mono text-gray-400 uppercase">Slurm Job Template</label>
                <select
                  value={submitTemplate}
                  onChange={(e) => setSubmitTemplate(e.target.value)}
                  className="w-full mt-1 bg-black/50 border border-white/10 rounded px-2 py-1.5 text-xs font-mono text-gray-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="jobs/gpu_training.slurm">jobs/gpu_training.slurm (NVIDIA GPU)</option>
                  <option value="jobs/llm_finetune.slurm">jobs/llm_finetune.slurm (QLoRA 14B)</option>
                  <option value="jobs/cpu_backtest.slurm">jobs/cpu_backtest.slurm (32 Core Parallel)</option>
                  <option value="jobs/large_memory.slurm">jobs/large_memory.slurm (128GB RAM)</option>
                  <option value="jobs/embedding_generation.slurm">jobs/embedding_generation.slurm</option>
                  <option value="jobs/monte_carlo.slurm">jobs/monte_carlo.slurm (100k Paths)</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] font-mono text-gray-400 uppercase">Compute Target</label>
                <select
                  value={submitTarget}
                  onChange={(e) => setSubmitTarget(e.target.value)}
                  className="w-full mt-1 bg-black/50 border border-white/10 rounded px-2 py-1.5 text-xs font-mono text-gray-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="UNITY_GPU">UNITY_GPU (uri-gpu Partition)</option>
                  <option value="UNITY_CPU">UNITY_CPU (uri-cpu Partition)</option>
                  <option value="UNITY_HIGHMEM">UNITY_HIGHMEM (large-mem Partition)</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] font-mono text-gray-400 uppercase">Experiment ID (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. EXP_ALPHA_B_HOLDING_SWEEP"
                  value={submitExpId}
                  onChange={(e) => setSubmitExpId(e.target.value)}
                  className="w-full mt-1 bg-black/50 border border-white/10 rounded px-2 py-1.5 text-xs font-mono text-gray-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition-all shadow-md shadow-cyan-600/20"
                >
                  <Play className="w-3 h-3" />
                  <span>{submitting ? 'Submitting...' : 'Launch Job'}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Jobs Table */}
          <div className="glass-panel overflow-hidden">
            <div className="p-3.5 border-b border-white/10 flex items-center justify-between">
              <span className="text-xs font-bold font-mono text-white">Active & Recent Slurm Jobs</span>
              <span className="text-[10px] font-mono text-gray-400">Cluster Path: /scratch3/.../MM/</span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Job Name</th>
                  <th>Partition</th>
                  <th>Status</th>
                  <th>Nodes / CPUs</th>
                  <th>Runtime</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-6 text-xs text-gray-500 font-mono">
                      No active Slurm jobs found on cluster.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.job_id}>
                      <td className="font-mono font-bold text-cyan-400 text-xs">{job.job_id}</td>
                      <td className="font-mono text-white text-xs">{job.job_name}</td>
                      <td className="font-mono text-gray-400 text-xs">{job.partition}</td>
                      <td>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                            job.status === 'RUNNING'
                              ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30 animate-pulse'
                              : job.status === 'COMPLETED'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                              : 'bg-amber-950 text-amber-400 border border-amber-500/30'
                          }`}
                        >
                          {job.status}
                        </span>
                      </td>
                      <td className="font-mono text-gray-300 text-xs">
                        {job.nodes} node / {job.cpus} cpus
                      </td>
                      <td className="font-mono text-gray-400 text-xs">{job.runtime}</td>
                      <td className="flex items-center gap-2">
                        <button
                          onClick={() => handleViewLogs(job.job_id)}
                          className="px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-xs font-mono text-gray-300 border border-white/10"
                        >
                          Logs
                        </button>
                        {job.status === 'RUNNING' && (
                          <button
                            onClick={() => handleCancelJob(job.job_id)}
                            className="px-2 py-1 rounded bg-rose-950 hover:bg-rose-900 text-xs font-mono text-rose-300 border border-rose-500/30"
                          >
                            Cancel
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* B. EXPERIMENT REGISTRY */}
      {activeSubTab === 'experiments' && (
        <div className="glass-panel overflow-hidden">
          <div className="p-3.5 border-b border-white/10 flex items-center justify-between">
            <span className="text-xs font-bold font-mono text-white">Cryptographic Experiment Ledger</span>
            <span className="text-[10px] font-mono text-gray-400">Total Experiments: {experiments.length}</span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Experiment ID</th>
                <th>Strategy</th>
                <th>Target</th>
                <th>Status</th>
                <th>Dataset / Config Hash</th>
                <th>Metrics</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {experiments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-6 text-xs text-gray-500 font-mono">
                    No experiments registered yet.
                  </td>
                </tr>
              ) : (
                experiments.map((exp) => (
                  <tr key={exp.experiment_id}>
                    <td className="font-mono font-bold text-white text-xs">{exp.experiment_id}</td>
                    <td className="font-mono text-cyan-400 text-xs">{exp.strategy_id}</td>
                    <td className="font-mono text-gray-400 text-xs">{exp.compute_target}</td>
                    <td>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                          exp.status === 'APPROVED' || exp.status === 'COMPLETED'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                            : exp.status === 'RUNNING'
                            ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                            : exp.status === 'REJECTED' || exp.status === 'FAILED'
                            ? 'bg-rose-950 text-rose-400 border border-rose-500/30'
                            : 'bg-amber-950 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {exp.status}
                      </span>
                    </td>
                    <td className="font-mono text-[10px] text-gray-400">
                      <div>DS: {exp.dataset_hash.slice(0, 10)}...</div>
                      <div>CFG: {exp.config_hash.slice(0, 10)}...</div>
                    </td>
                    <td className="font-mono text-xs text-gray-300">
                      {Object.entries(exp.metrics || {})
                        .slice(0, 2)
                        .map(([k, v]) => `${k}: ${typeof v === 'number' ? v.toFixed(3) : v}`)
                        .join(' | ') || 'Pending'}
                    </td>
                    <td className="font-mono text-gray-400 text-xs">
                      {new Date(exp.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* C. MODEL REGISTRY & BENCHMARKS */}
      {activeSubTab === 'models' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models.map((model) => (
              <div
                key={model.model_id}
                className={`glass-panel p-4 space-y-3 ${
                  model.is_workstation_active ? 'border-cyan-500/40' : 'border-white/10'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold font-mono text-white flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-cyan-400" />
                      {model.model_id}
                    </div>
                    <div className="text-xs font-mono text-gray-400">{model.base_model_name}</div>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                      model.approval_state === 'VALIDATED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                        : model.approval_state === 'CANDIDATE'
                        ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                        : 'bg-amber-950 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {model.approval_state}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                  <div className="p-2 rounded bg-black/30 border border-white/5">
                    <span className="text-gray-400 text-[10px]">BENCHMARK SCORE</span>
                    <div className="text-lg font-bold text-cyan-300">{model.benchmark_score.toFixed(1)} / 100</div>
                  </div>
                  <div className="p-2 rounded bg-black/30 border border-white/5">
                    <span className="text-gray-400 text-[10px]">WORKSTATION ACTIVE</span>
                    <div className="text-sm font-bold text-white">
                      {model.is_workstation_active ? 'PRODUCTION' : 'RESEARCH CANDIDATE'}
                    </div>
                  </div>
                </div>

                <div className="space-y-1 font-mono text-xs">
                  <div className="text-[10px] text-gray-400 uppercase">Domain Benchmark Breakdown</div>
                  {Object.entries(model.benchmark_details || {}).map(([k, v]) => (
                    <div key={k} className="flex justify-between items-center text-gray-300">
                      <span className="text-[11px] capitalize">{k.replace('_', ' ')}:</span>
                      <span className="text-cyan-400 font-bold">{typeof v === 'number' ? v.toFixed(1) : v}%</span>
                    </div>
                  ))}
                </div>

                <div className="pt-2 border-t border-white/5 font-mono text-[10px] text-gray-400 flex justify-between items-center">
                  <span>Checkpoint: <span className="text-gray-300">{model.checkpoint_path}</span></span>
                  <button
                    onClick={() => handleAuditModel(model.model_id)}
                    className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-[10px] hover:bg-cyan-900"
                  >
                    Audit Provenance
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* D. A/B MODEL EVALUATION & 4-WAY BENCHMARK */}
      {activeSubTab === 'ab_eval' && (
        <div className="space-y-4">
          {/* Prompt Form */}
          <div className="glass-panel p-4 space-y-3">
            <div className="text-xs font-bold font-mono text-white flex items-center gap-2">
              <GitCompare className="w-4 h-4 text-cyan-400" />
              CONTROLLED COPILOT A/B COMPARISON: BASE QWEN 2.5 14B vs. MMRM-0.1 (QLoRA)
            </div>
            <form onSubmit={handleRunAB} className="flex gap-2">
              <input
                type="text"
                value={abPrompt}
                onChange={(e) => setAbPrompt(e.target.value)}
                placeholder="Enter quantitative question (e.g. Why did we buy AMD? How healthy is Alpha A?)..."
                className="flex-1 bg-black/50 border border-white/10 rounded px-3 py-2 text-xs font-mono text-gray-200 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                disabled={abLoading}
                className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition-all shadow-md shadow-cyan-600/20 flex items-center gap-1.5"
              >
                <Play className={`w-3.5 h-3.5 ${abLoading ? 'animate-spin' : ''}`} />
                <span>{abLoading ? 'Evaluating...' : 'Run A/B Compare'}</span>
              </button>
            </form>
          </div>

          {/* Side-by-Side Response Viewer */}
          {abResult && (
            <div className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Base Response */}
                <div className="glass-panel p-4 space-y-2 border-white/10">
                  <div className="flex justify-between items-center border-b border-white/10 pb-2">
                    <span className="text-xs font-bold font-mono text-gray-300">
                      1. BASE MODEL (Qwen2.5-14B-Instruct)
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-900 text-gray-400 border border-white/10">
                      Zero-Shot Baseline
                    </span>
                  </div>
                  <div className="text-xs font-mono text-gray-300 leading-relaxed whitespace-pre-wrap">
                    {abResult.base_response.reply}
                  </div>
                  <div className="pt-2 border-t border-white/5 text-[10px] font-mono text-gray-500">
                    Tools: {abResult.base_response.tool_calls.map((t) => t.tool_name).join(', ') || 'None'}
                  </div>
                </div>

                {/* MMRM-0.1 Response */}
                <div className="glass-panel p-4 space-y-2 border-cyan-500/40 bg-cyan-950/10">
                  <div className="flex justify-between items-center border-b border-white/10 pb-2">
                    <span className="text-xs font-bold font-mono text-cyan-300 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      2. MMRM-0.1 (Domain QLoRA Fine-Tune)
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/30 font-bold">
                      Domain Fine-Tuned
                    </span>
                  </div>
                  <div className="text-xs font-mono text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {abResult.mmrm_response.reply}
                  </div>
                  <div className="pt-2 border-t border-white/5 text-[10px] font-mono text-cyan-400">
                    Tools: {abResult.mmrm_response.tool_calls.map((t) => t.tool_name).join(', ') || 'None'} | Badge: {abResult.mmrm_response.evidence_badge}
                  </div>
                </div>
              </div>

              {/* RAG Context Panel */}
              {abResult.rag_context && (
                <div className="p-2.5 rounded bg-black/40 border border-white/5 text-[11px] font-mono text-gray-400">
                  <span className="text-cyan-400 font-bold">Retrieved Grounding Memory:</span> {abResult.rag_context}
                </div>
              )}

              {/* Human Evaluation Feedback Buttons */}
              <div className="glass-panel p-3 flex items-center justify-between font-mono text-xs">
                <span className="text-gray-300 font-bold">Record Human Evaluation Verdict:</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleFeedback('MMRM_BETTER')}
                    className="px-3 py-1 rounded bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-500/40 text-xs font-bold flex items-center gap-1"
                  >
                    <ThumbsUp className="w-3 h-3 text-cyan-400" />
                    MMRM Better
                  </button>
                  <button
                    onClick={() => handleFeedback('BASE_BETTER')}
                    className="px-3 py-1 rounded bg-gray-900 hover:bg-gray-800 text-gray-300 border border-white/10 text-xs flex items-center gap-1"
                  >
                    <ThumbsDown className="w-3 h-3 text-gray-400" />
                    Base Better
                  </button>
                  <button
                    onClick={() => handleFeedback('EQUAL')}
                    className="px-3 py-1 rounded bg-black/40 hover:bg-black/60 text-gray-400 border border-white/10 text-xs"
                  >
                    Equal / Tie
                  </button>
                  <button
                    onClick={() => handleFeedback('BOTH_BAD')}
                    className="px-3 py-1 rounded bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-500/30 text-xs"
                  >
                    Both Deficient
                  </button>
                </div>
                {abFeedbackStatus && (
                  <span className="text-emerald-400 text-xs font-bold">{abFeedbackStatus}</span>
                )}
              </div>
            </div>
          )}

          {/* 4-Way System Comparison Matrix */}
          {fourWayMatrix && (
            <div className="glass-panel overflow-hidden">
              <div className="p-3.5 border-b border-white/10 flex items-center justify-between font-mono">
                <span className="text-xs font-bold text-white">4-Way Empirical System Benchmark Matrix</span>
                <span className="text-[10px] text-emerald-400 font-bold">
                  McNemar Significance: p = {fourWayMatrix.statistical_significance.mcnemar_p_value_base_vs_mmrm}
                </span>
              </div>
              <table className="data-table font-mono text-xs">
                <thead>
                  <tr>
                    <th>System Configuration</th>
                    <th>Overall Score</th>
                    <th>Tool Accuracy</th>
                    <th>Hallucination Rate</th>
                    <th>Provenance Accuracy</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(fourWayMatrix.comparison_matrix).map(([sys, row]) => (
                    <tr key={sys}>
                      <td className="font-bold text-white">{sys.replace(/_/g, ' ')}</td>
                      <td className="text-cyan-400 font-bold">{row.overall_score.toFixed(1)}%</td>
                      <td className="text-gray-300">{row.tool_accuracy.toFixed(1)}%</td>
                      <td className={row.hallucination_rate < 5 ? 'text-emerald-400 font-bold' : 'text-amber-400'}>
                        {row.hallucination_rate.toFixed(1)}%
                      </td>
                      <td className="text-cyan-300">{row.provenance_accuracy.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}


      {/* D. DATASETS & MANIFESTS */}
      {activeSubTab === 'datasets' && (
        <div className="glass-panel overflow-hidden">
          <div className="p-3.5 border-b border-white/10 flex items-center justify-between">
            <span className="text-xs font-bold font-mono text-white">Immutable Point-in-Time Research Datasets</span>
            <span className="text-[10px] font-mono text-gray-400">Leakage & Lookahead Protected</span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Dataset ID</th>
                <th>Date Range</th>
                <th>Frequency</th>
                <th>Symbols</th>
                <th>Rows</th>
                <th>Embargo</th>
                <th>Dataset Hash</th>
              </tr>
            </thead>
            <tbody>
              {datasets.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-6 text-xs text-gray-500 font-mono">
                    No dataset manifests found.
                  </td>
                </tr>
              ) : (
                datasets.map((ds) => (
                  <tr key={ds.dataset_id}>
                    <td className="font-mono font-bold text-white text-xs">{ds.dataset_id}</td>
                    <td className="font-mono text-gray-300 text-xs">
                      {ds.start_date} → {ds.end_date}
                    </td>
                    <td className="font-mono text-cyan-400 text-xs">{ds.bar_frequency}</td>
                    <td className="font-mono text-gray-300 text-xs">{ds.symbols.slice(0, 4).join(', ')}...</td>
                    <td className="font-mono text-gray-300 text-xs">{ds.row_count.toLocaleString()}</td>
                    <td className="font-mono text-amber-400 text-xs">{ds.embargo_bars} bars</td>
                    <td className="font-mono text-[10px] text-gray-400">{ds.dataset_hash.slice(0, 12)}...</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* E. RESEARCH MEMORY (RAG) */}
      {activeSubTab === 'memory' && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search research reports, capacity findings, incident logs, model cards..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-md pl-9 pr-3 py-2 text-xs font-mono text-gray-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {memoryDocs.map((doc) => (
              <div key={doc.document_id} className="glass-panel p-3.5 space-y-2 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-white font-bold text-xs">{doc.title}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-cyan-300 border border-white/10">
                    {doc.document_type}
                  </span>
                </div>
                <div className="text-gray-400 text-[11px] line-clamp-3 leading-relaxed">
                  {doc.content}
                </div>
                <div className="flex justify-between items-center text-[10px] text-gray-500 pt-1 border-t border-white/5">
                  <span>Strategy: {doc.strategy || 'PLATFORM'}</span>
                  <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LOGS MODAL */}
      {selectedLogs && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <div className="bg-[#0b0e17] border border-white/20 rounded-lg max-w-2xl w-full p-4 space-y-3 font-mono">
            <div className="flex items-center justify-between border-b border-white/10 pb-2">
              <span className="text-xs font-bold text-cyan-400">
                SLURM JOB LOGS: {selectedLogs.jobId}
              </span>
              <button
                onClick={() => setSelectedLogs(null)}
                className="text-gray-400 hover:text-white text-xs"
              >
                ✕ Close
              </button>
            </div>
            <pre className="bg-black/70 p-3 rounded text-xs text-emerald-400 max-h-96 overflow-y-auto font-mono whitespace-pre-wrap">
              {selectedLogs.logs}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
