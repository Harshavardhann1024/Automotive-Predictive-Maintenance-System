import { useEffect, useState } from "react";
import { fetchDashboardSummary, fetchAlerts, fetchSystemStatus } from "../services/api";

export default function useDashboardData() {
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState({ healthy: false, message: "Loading" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = async () => {
    setLoading(true);
    setError("");

    try {
      const [summaryData, alertsData, systemStatus] = await Promise.all([
        fetchDashboardSummary(),
        fetchAlerts(),
        fetchSystemStatus()
      ]);
      setSummary(summaryData);
      setAlerts(alertsData);
      setStatus(systemStatus);
      setError("");
    } catch (err) {
      setError(err?.message || "Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return {
    summary,
    alerts,
    status,
    loading,
    error,
    refresh
  };
}
