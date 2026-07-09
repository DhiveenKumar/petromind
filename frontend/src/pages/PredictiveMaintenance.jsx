import { useState } from "react";
import { TrendingUp, AlertCircle, Loader2, Zap, Upload, FileSpreadsheet } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api/client";

export default function PredictiveMaintenance() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [equipmentName, setEquipmentName] = useState("Pump-17");

  const riskColor = {
    HIGH: "#ef4444",
    MEDIUM: "#f59e0b",
    LOW: "#10b981"
  };

  const runSample = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPredictionSample();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runUpload = async () => {
    if (!file) {
      setError("Please select a CSV file first");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.analysePrediction(file, equipmentName);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      setError(null);
    }
  };

  const sensorData = result?.sensor_summary
    ? Object.entries(result.sensor_summary).map(([name, stats]) => ({
        name: name.replace("_", " "),
        anomalies: stats.anomaly_count,
        trend: stats.trend_percent
      }))
    : [];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <div className="text-xs font-bold tracking-widest text-[#f59e0b] uppercase mb-1">
          Time Series Transformer + LLM
        </div>
        <h1 className="text-3xl font-bold text-white">Predictive Maintenance</h1>
        <p className="text-[#a89a8c] text-sm mt-1">
          Anomaly detection on equipment sensor data with explainable AI
        </p>
      </div>

      {!result && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-8 text-center">
            <TrendingUp size={28} className="text-[#f59e0b] mx-auto mb-3" />
            <div className="text-sm font-semibold text-white mb-1">Try With Sample Data</div>
            <p className="text-xs text-[#a89a8c] mb-5">
              Synthetic sensor data with pre-injected anomalies
            </p>
            <button
              onClick={runSample}
              disabled={loading}
              className="px-5 py-2.5 bg-gradient-to-r from-[#d97706] to-[#f59e0b] rounded-lg text-[#0a0908] font-semibold text-sm inline-flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 size={15} className="animate-spin" /> : <Zap size={15} />}
              {loading ? "Analysing..." : "Run Sample Analysis"}
            </button>
          </div>

          <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-8 text-center">
            <Upload size={28} className="text-[#f59e0b] mx-auto mb-3" />
            <div className="text-sm font-semibold text-white mb-1">Upload Your Own CSV</div>
            <p className="text-xs text-[#a89a8c] mb-4">
              Columns: timestamp, pressure_psi, temperature_f, vibration_mm
            </p>

            <input
              value={equipmentName}
              onChange={(e) => setEquipmentName(e.target.value)}
              placeholder="Equipment name"
              className="w-full bg-[#0a0908] border border-[#332b26] rounded-lg px-3 py-2 text-sm text-white placeholder-[#a89a8c] focus:outline-none focus:border-[#d97706]/50 mb-3"
            />

            <label className="flex items-center justify-center gap-2 border border-dashed border-[#332b26] rounded-lg py-2.5 cursor-pointer hover:border-[#d97706]/40 transition-colors mb-3">
              <FileSpreadsheet size={15} className="text-[#a89a8c]" />
              <span className="text-xs text-[#a89a8c]">
                {file ? file.name : "Choose CSV file"}
              </span>
              <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
            </label>

            <button
              onClick={runUpload}
              disabled={loading || !file}
              className="w-full px-5 py-2.5 bg-[#241f1c] border border-[#d97706]/30 rounded-lg text-[#f59e0b] font-semibold text-sm inline-flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 size={15} className="animate-spin" /> : <Upload size={15} />}
              {loading ? "Analysing..." : "Analyse My Data"}
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-[#ef4444]/10 border border-[#ef4444]/30 rounded-xl p-4 text-sm text-[#ef4444] mt-4">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
              <div className="text-xs text-[#a89a8c] mb-1">Equipment</div>
              <div className="text-lg font-bold text-white">{result.equipment_name}</div>
            </div>
            <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
              <div className="text-xs text-[#a89a8c] mb-1">Risk Level</div>
              <div className="text-lg font-bold" style={{ color: riskColor[result.risk_level] }}>
                {result.risk_level}
              </div>
            </div>
            <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
              <div className="text-xs text-[#a89a8c] mb-1">Failure Probability</div>
              <div className="text-lg font-bold text-white">
                {Math.round(result.failure_probability * 100)}%
              </div>
            </div>
          </div>

          <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
            <div className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide mb-4">
              Sensor Anomalies
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={sensorData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#332b26" />
                <XAxis dataKey="name" stroke="#a89a8c" fontSize={12} />
                <YAxis stroke="#a89a8c" fontSize={12} />
                <Tooltip contentStyle={{ background: "#1a1614", border: "1px solid #332b26", borderRadius: 8 }} />
                <Line type="monotone" dataKey="trend" stroke="#f59e0b" strokeWidth={2} dot={{ fill: "#f59e0b" }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle size={16} className="text-[#f59e0b]" />
              <span className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide">
                LLM Engineering Analysis
              </span>
            </div>
            <div className="text-sm text-[#e8e3dc] leading-relaxed whitespace-pre-wrap">
              {result.llm_explanation}
            </div>
          </div>

          <button
            onClick={() => { setResult(null); setFile(null); }}
            className="text-sm text-[#a89a8c] hover:text-[#e8e3dc]"
          >
            ← Run another analysis
          </button>
        </div>
      )}
    </div>
  );
}
