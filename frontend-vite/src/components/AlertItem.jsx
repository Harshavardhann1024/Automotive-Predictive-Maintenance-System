import React from "react";

export default function AlertItem({ alert }) {
  const severityClass = alert.severity?.toLowerCase?.() || "unknown";
  return (
    <li className={`alert-item ${severityClass}`}>
      <strong>{alert.alert_type || "Alert"} </strong>
      <span>{alert.message || "No details"}</span>
      <small>{new Date(alert.created_at).toLocaleString()}</small>
    </li>
  );
}
