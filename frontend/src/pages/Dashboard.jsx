import { useEffect, useState } from "react";
import { Database, Cpu, Activity, AlertTriangle, CheckCircle2, Zap } from "lucide-react";
import { api } from "../api/client";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.health()
      .then(setHealth)
      .catch(() => setHealth({ status: "error" }))
      .finally(() => setLoading(false));
  }, []);

  const kpis = [
    {
      label: "Documents Indexed",
      value: health?.services?.qdrant?.chunks || "—",
      icon: Database,
      suffix: "chunks"
    },
    {
      label: "AI Modules Active",
      value: "3",
      icon: Cpu,
      suffix: "modules"
    },
    {
      label: "System Status",
      value: health?.status === "healthy" ? "Healthy" : "Checking...",
      icon: health?.status === "healthy" ? CheckCircle2 : AlertTriangle,
      isStatus: true
    },
    {
      label: "Response Latency",
      value: health?.latency_ms ? Math.round(health.latency_ms) : "—",
      icon: Zap,
      suffix: "ms"
    },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="text-xs font-bold tracking-widest text-[#f59e0b] uppercase mb-1">
          Enterprise AI Platform
        </div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-[#a89a8c] text-sm mt-1">
          Oil & Gas Operations — Real-time AI System Overview
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {kpis.map((kpi, i) => (
          <div key={i} className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <kpi.icon size={18} className={kpi.isStatus && health?.status === "healthy" ? "text-[#10b981]" : "text-[#f59e0b]"} />
            </div>
            <div className={`text-2xl font-bold ${kpi.isStatus ? (health?.status === "healthy" ? "text-[#10b981]" : "text-[#ef4444]") : "text-white"}`}>
              {loading ? "..." : kpi.value}
              {kpi.suffix && <span className="text-sm text-[#a89a8c] ml-1 font-normal">{kpi.suffix}</span>}
            </div>
            <div className="text-xs text-[#a89a8c] mt-1">{kpi.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full bg-[#f59e0b]" />
            <span className="text-sm font-semibold text-white">Knowledge AI</span>
          </div>
          <p className="text-xs text-[#a89a8c] leading-relaxed">
            Qdrant vector database + LangGraph agentic RAG. Answers grounded in technical documentation with citations.
          </p>
        </div>
        <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full bg-[#f59e0b]" />
            <span className="text-sm font-semibold text-white">Prediction AI</span>
          </div>
          <p className="text-xs text-[#a89a8c] leading-relaxed">
            Time series anomaly detection combined with LLM explanation for explainable failure forecasting.
          </p>
        </div>
        <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full bg-[#f59e0b]" />
            <span className="text-sm font-semibold text-white">Vision AI</span>
          </div>
          <p className="text-xs text-[#a89a8c] leading-relaxed">
            Equipment defect detection with LLM severity reasoning and compliance-cited recommendations.
          </p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-[#1a1614] to-[#241f1c] border border-[#d97706]/20 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <Activity size={20} className="text-[#f59e0b] mt-0.5" />
          <div>
            <div className="font-semibold text-white text-sm mb-1">Decision Intelligence Engine</div>
            <p className="text-xs text-[#a89a8c] leading-relaxed">
              Synthesises findings across all three AI modules, resolves conflicting evidence, and autonomously executes actions — maintenance tickets, alerts, and inventory checks — based on priority reasoning.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
