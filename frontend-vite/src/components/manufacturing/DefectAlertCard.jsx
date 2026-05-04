import React from "react";

export default function DefectAlertCard({ insight }) {
  return (
    <div className="card-panel">
      <h3>{insight.issue}</h3>
      <p>Affected vehicles: {insight.vehicles_impacted}</p>
      <p>Batch risk score: {insight.risk_score}</p>
    </div>
  );
}
