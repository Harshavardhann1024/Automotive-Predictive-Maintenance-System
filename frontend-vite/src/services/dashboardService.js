const API_BASE = "http://127.0.0.1:8000";

export const getDashboardSummary = async () => {
  const response = await fetch(`${API_BASE}/dashboard/api/dashboard/summary`);
  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard summary (${response.status})`);
  }
  return response.json();
};

export const getRecentAlerts = async (limit = 10) => {
  const response = await fetch(`${API_BASE}/dashboard/api/alerts/recent?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch recent alerts (${response.status})`);
  }
  return response.json();
};
