import { useState } from "react";
import { FileText, Loader2, CheckCircle2, Ticket, Bell, Package } from "lucide-react";
import { api } from "../api/client";

export default function UnifiedReport() {
  const [equipmentName, setEquipmentName] = useState("Pump-17");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const knowledgeResult = {
        answer: "API 610 Section 8.3 indicates seal failure risk at vibration levels above 6mm.",
        sources: ["API_610.pdf, Page 47"]
      };
      const predictionResult = {
        risk_level: "HIGH",
        failure_probability: 0.95,
        llm_explanation: "Vibration increased 69%, pressure spiked 8.5%, bearing failure likely within 24-48 hours."
      };
      const visionResult = {
        severity_level: "MEDIUM",
        severity_assessment: "Corrosion detected on outlet flange covering 15% of surface."
      };

      const data = await api.generateReport(equipmentName, knowledgeResult, predictionResult, visionResult);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toolIcons = {
    create_maintenance_ticket: Ticket,
    send_alert: Bell,
    check_spare_parts_inventory: Package
  };

  const priorityColor = (score) => {
    if (score >= 8) return "#ef4444";
    if (score >= 5) return "#f59e0b";
    return "#10b981";
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <div className="text-xs font-bold tracking-widest text-[#f59e0b] uppercase mb-1">
          Decision Intelligence Engine
        </div>
        <h1 className="text-3xl font-bold text-white">Unified AI Report</h1>
        <p className="text-[#a89a8c] text-sm mt-1">
          Cross-modal synthesis with autonomous action execution
        </p>
      </div>

      {!result && (
        <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-8">
          <div className="mb-5">
            <label className="text-xs text-[#a89a8c] mb-2 block">Equipment Name</label>
            <input
              value={equipmentName}
              onChange={(e) => setEquipmentName(e.target.value)}
              className="w-full bg-[#0a0908] border border-[#332b26] rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-[#d97706]/50"
            />
          </div>
          <p className="text-xs text-[#a89a8c] mb-5 leading-relaxed">
            This demo combines simulated findings from Knowledge AI, Prediction AI, and Vision AI —
            the Decision Intelligence Engine will synthesise them, assign a priority score, generate
            an executive report, and autonomously execute maintenance actions.
          </p>
          <button
            onClick={runDemo}
            disabled={loading}
            className="w-full px-5 py-3 bg-gradient-to-r from-[#d97706] to-[#f59e0b] rounded-lg text-[#0a0908] font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
            {loading ? "Synthesising across 3 AI modules..." : "Generate Unified Report"}
          </button>
        </div>
      )}

      {error && (
        <div className="bg-[#ef4444]/10 border border-[#ef4444]/30 rounded-xl p-4 text-sm text-[#ef4444] mb-6">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="flex items-center justify-between bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
            <div>
              <div className="text-xs text-[#a89a8c]">Equipment</div>
              <div className="text-lg font-bold text-white">{result.equipment_name}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-[#a89a8c]">Priority Score</div>
              <div className="text-2xl font-bold" style={{ color: priorityColor(result.priority_score) }}>
                {result.priority_score}/10
              </div>
            </div>
          </div>

          {result.actions_taken && result.actions_taken.length > 0 && (
            <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 size={16} className="text-[#10b981]" />
                <span className="text-xs font-semibold text-[#10b981] uppercase tracking-wide">
                  Autonomous Actions Executed — {result.actions_taken.length}
                </span>
              </div>
              <div className="space-y-2">
                {result.actions_taken.map((action, i) => {
                  const Icon = toolIcons[action.tool] || CheckCircle2;
                  return (
                    <div key={i} className="flex items-start gap-3 bg-[#0a0908] border border-[#332b26] rounded-lg p-3">
                      <Icon size={16} className="text-[#f59e0b] mt-0.5" />
                      <div>
                        <div className="text-xs font-semibold text-white capitalize">
                          {action.tool.replace(/_/g, " ")}
                        </div>
                        <div className="text-xs text-[#a89a8c] mt-0.5">{action.result}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-6">
            <div className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide mb-4">
              Executive Report
            </div>
            <div className="text-sm text-[#e8e3dc] leading-relaxed whitespace-pre-wrap prose-sm">
              {result.executive_report}
            </div>
          </div>

          <div className="text-xs text-[#a89a8c]">
            Generated in {result.latency_seconds}s · Modules: {result.modules_used?.join(", ")}
          </div>

          <button
            onClick={() => setResult(null)}
            className="text-sm text-[#a89a8c] hover:text-[#e8e3dc]"
          >
            ← Generate another report
          </button>
        </div>
      )}
    </div>
  );
}
