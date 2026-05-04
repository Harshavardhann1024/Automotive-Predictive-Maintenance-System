import React from "react";
import Badge from "../common/Badge";

export default function AlertsPanel({ alerts = [] }) {
  if (!alerts.length) {
    return <div className="empty-state">No alerts in the last 24 hours.</div>;
  }

  return (
    <section className="alerts-panel">
      <header>
        <h2>Recent Alerts</h2>
        <span>{alerts.length} items</span>
      </header>
      <ul>
        {alerts.slice(0, 6).map((alert) => (
          <li key={alert.id} className="alerts-row">
            <div>
              <p className="alert-message">{alert.message}</p>
              <small>Vehicle: {alert.vehicle_id} • {new Date(alert.created_at).toLocaleString()}</small>
            </div>
            <div className="alert-badges">
              <Badge>{alert.status}</Badge>
              <Badge>{alert.severity}</Badge>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
