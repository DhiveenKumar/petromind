const API_BASE = import.meta.env.VITE_API_URL || "https://petromind-642904158062.us-central1.run.app";

const TOKENS = {
  field_engineer: "field_token_123",
  maintenance_manager: "manager_token_456",
  administrator: "admin_token_789"
};

let currentRole = "field_engineer";

export function setRole(role) {
  currentRole = role;
}

export function getRole() {
  return currentRole;
}

async function apiCall(endpoint, options = {}) {
  const token = TOKENS[currentRole];
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Authorization": `Bearer ${token}`,
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...options.headers
    }
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  health: () => apiCall("/health"),

  getMe: () => apiCall("/api/auth/me"),

  getRoles: () => apiCall("/api/auth/roles"),

  queryKnowledge: (query) =>
    apiCall("/api/knowledge/query", {
      method: "POST",
      body: JSON.stringify({ query })
    }),

  getPredictionSample: () => apiCall("/api/prediction/sample"),

  analysePrediction: (file, equipmentName) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("equipment_name", equipmentName);
    return apiCall("/api/prediction/analyse", {
      method: "POST",
      body: formData
    });
  },

  analyseVision: (file, equipmentName, sensorContext) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("equipment_name", equipmentName);
    if (sensorContext) formData.append("sensor_context", sensorContext);
    return apiCall("/api/vision/analyse", {
      method: "POST",
      body: formData
    });
  },

  generateReport: (equipmentName, knowledgeResult, predictionResult, visionResult) =>
    apiCall("/api/report/generate", {
      method: "POST",
      body: JSON.stringify({
        equipment_name: equipmentName,
        knowledge_result: knowledgeResult || null,
        prediction_result: predictionResult || null,
        vision_result: visionResult || null
      })
    })
};
