import React from "react";
import AlertItem from "./AlertItem";

export default function AlertPanel({ alerts }) {
  if (!Array.isArray(alerts) || alerts.length === 0) {
    return <div className="panel-empty">No recent alerts found.</div>;
  }
  return (
    <section className="alert-panel">
      <h2>Recent Alerts</h2>
      <ul>
        {alerts.map((alert) => (
          <AlertItem key={alert.id || `${alert.vehicle_id}-${alert.created_at}`} alert={alert} />
        ))}
      </ul>
    </section>
  );
}
