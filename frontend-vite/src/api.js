const API_BASE = "http://127.0.0.1:8000";

export const getVehicles = async () => {
  const res = await fetch(`${API_BASE}/vehicles`);
  if (!res.ok) throw new Error("Failed to fetch vehicles");
  return res.json();
};