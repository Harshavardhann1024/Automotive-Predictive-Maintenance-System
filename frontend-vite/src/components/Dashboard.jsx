import React from "react";
import StatCard from "./StatCard";
import AlertPanel from "./AlertPanel";

const ICONS = {
  totalVehicles: "🚗",
  activeAlerts: "⚠️",
  totalPredictions: "📈",
  recentReadings: "🔧"
};

export default function Dashboard({ summary, alerts, loading, error, onRefresh }) {
  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <h1>Automotive Predictive Maintenance</h1>
          <p>Production-ready modular dashboard with real-time metrics.</p>
        </div>
        <button className="refresh-button" onClick={onRefresh} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </header>

      {error && <div className="dashboard-error">{error}</div>}

      <section className="stats-grid" aria-live="polite">
        <StatCard label="Total Vehicles" value={summary?.total_vehicles ?? "—"} icon={ICONS.totalVehicles} />
        <StatCard label="Active Alerts" value={summary?.active_alerts ?? "—"} icon={ICONS.activeAlerts} />
        <StatCard label="Total Predictions" value={summary?.total_predictions ?? "—"} icon={ICONS.totalPredictions} />
        <StatCard label="Recent Readings (24h)" value={summary?.recent_readings ?? "—"} icon={ICONS.recentReadings} />
      </section>

      <AlertPanel alerts={alerts} />

      <footer className="dashboard-footer">
        <small>Last update: {summary?.timestamp ? new Date(summary.timestamp).toLocaleString() : "Never"}</small>
      </footer>
    </main>
  );
}
