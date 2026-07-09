import { useState } from "react";
import { Camera, Upload, Loader2, ShieldAlert } from "lucide-react";
import { api } from "../api/client";

export default function VisualInspection() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [equipmentName, setEquipmentName] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResult(null);
    }
  };

  const handleAnalyse = async () => {
    if (!file || !equipmentName) {
      setError("Please provide equipment name and select an image");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyseVision(file, equipmentName);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const severityColor = {
    CRITICAL: "#ef4444",
    HIGH: "#f59e0b",
    MEDIUM: "#f59e0b",
    LOW: "#10b981"
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <div className="text-xs font-bold tracking-widest text-[#f59e0b] uppercase mb-1">
          Vision AI + LLM Severity Reasoning
        </div>
        <h1 className="text-3xl font-bold text-white">Visual Inspection</h1>
        <p className="text-[#a89a8c] text-sm mt-1">
          Upload equipment photos for defect detection and severity analysis
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
            <label className="text-xs text-[#a89a8c] mb-2 block">Equipment Name</label>
            <input
              value={equipmentName}
              onChange={(e) => setEquipmentName(e.target.value)}
              placeholder="e.g. Pump-17"
              className="w-full bg-[#0a0908] border border-[#332b26] rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#a89a8c] focus:outline-none focus:border-[#d97706]/50 mb-4"
            />

            <label className="text-xs text-[#a89a8c] mb-2 block">Equipment Photo</label>
            <label className="flex flex-col items-center justify-center border-2 border-dashed border-[#332b26] rounded-lg h-40 cursor-pointer hover:border-[#d97706]/40 transition-colors overflow-hidden">
              {preview ? (
                <img src={preview} alt="preview" className="w-full h-full object-cover" />
              ) : (
                <>
                  <Upload size={24} className="text-[#a89a8c] mb-2" />
                  <span className="text-xs text-[#a89a8c]">Click to upload image</span>
                </>
              )}
              <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
            </label>

            <button
              onClick={handleAnalyse}
              disabled={loading}
              className="w-full mt-4 px-5 py-3 bg-gradient-to-r from-[#d97706] to-[#f59e0b] rounded-lg text-[#0a0908] font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Camera size={16} />}
              {loading ? "Analysing..." : "Analyse Image"}
            </button>

            {error && (
              <div className="mt-3 text-xs text-[#ef4444]">{error}</div>
            )}
          </div>
        </div>

        <div>
          {!result && (
            <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-10 h-full flex items-center justify-center text-center">
              <div>
                <ShieldAlert size={28} className="text-[#332b26] mx-auto mb-3" />
                <p className="text-sm text-[#a89a8c]">Analysis results will appear here</p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide">
                    Severity
                  </span>
                  <span
                    className="text-xs font-bold px-2.5 py-1 rounded-full"
                    style={{
                      color: severityColor[result.severity_level] || "#a89a8c",
                      backgroundColor: `${severityColor[result.severity_level]}15`
                    }}
                  >
                    {result.severity_level}
                  </span>
                </div>
              </div>

              <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5 max-h-96 overflow-y-auto">
                <div className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide mb-3">
                  Severity Assessment
                </div>
                <div className="text-sm text-[#e8e3dc] leading-relaxed whitespace-pre-wrap">
                  {result.severity_assessment}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
