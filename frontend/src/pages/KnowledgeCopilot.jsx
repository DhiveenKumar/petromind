import { useState } from "react";
import { Send, FileText, Loader2, MessageSquare } from "lucide-react";
import { api } from "../api/client";

export default function KnowledgeCopilot() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const exampleQuestions = [
    "What is the H2S exposure limit for workers?",
    "What are the IOGP Life Saving Rules for working at height?",
    "What must be done before entering a confined space?",
  ];

  const handleSubmit = async (q) => {
    const question = q || query;
    if (!question.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setQuery("");
    setLoading(true);

    try {
      const result = await api.queryKnowledge(question);
      setMessages((prev) => [...prev, { role: "assistant", ...result }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", content: err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto flex flex-col h-full">
      <div className="mb-6">
        <div className="text-xs font-bold tracking-widest text-[#f59e0b] uppercase mb-1">
          Agentic RAG
        </div>
        <h1 className="text-3xl font-bold text-white">Knowledge Copilot</h1>
        <p className="text-[#a89a8c] text-sm mt-1">
          Ask technical questions — answers cited from source documentation
        </p>
      </div>

      {messages.length === 0 && (
        <div className="mb-6">
          <div className="text-xs text-[#a89a8c] mb-3 uppercase tracking-wide">Try asking</div>
          <div className="space-y-2">
            {exampleQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSubmit(q)}
                className="block w-full text-left px-4 py-3 bg-[#1a1614] border border-[#332b26] rounded-lg text-sm text-[#a89a8c] hover:border-[#d97706]/40 hover:text-[#e8e3dc] transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex-1 space-y-4 mb-6 overflow-y-auto">
        {messages.map((msg, i) => (
          <div key={i}>
            {msg.role === "user" && (
              <div className="flex justify-end">
                <div className="bg-[#d97706]/10 border border-[#d97706]/30 rounded-xl px-4 py-2.5 max-w-lg text-sm text-white">
                  {msg.content}
                </div>
              </div>
            )}
            {msg.role === "assistant" && (
              <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare size={14} className="text-[#f59e0b]" />
                  <span className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide">
                    PetroMind Knowledge AI
                  </span>
                  <span className="text-xs text-[#a89a8c] ml-auto">
                    {msg.latency_seconds}s · {msg.chunks_retrieved} chunks
                  </span>
                </div>
                <p className="text-sm text-[#e8e3dc] leading-relaxed whitespace-pre-wrap">
                  {msg.answer}
                </p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-[#332b26]">
                    {msg.sources.map((source, si) => (
                      <div key={si} className="flex items-center gap-1.5 text-xs text-[#a89a8c] bg-[#241f1c] px-2.5 py-1 rounded-md">
                        <FileText size={11} />
                        {source}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            {msg.role === "error" && (
              <div className="bg-[#ef4444]/10 border border-[#ef4444]/30 rounded-xl p-4 text-sm text-[#ef4444]">
                {msg.content}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-[#a89a8c]">
            <Loader2 size={14} className="animate-spin" />
            Searching technical documentation...
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="Ask a technical question..."
          className="flex-1 bg-[#1a1614] border border-[#332b26] rounded-lg px-4 py-3 text-sm text-white placeholder-[#a89a8c] focus:outline-none focus:border-[#d97706]/50"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={loading}
          className="px-5 py-3 bg-gradient-to-r from-[#d97706] to-[#f59e0b] rounded-lg text-[#0a0908] font-semibold disabled:opacity-50"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
