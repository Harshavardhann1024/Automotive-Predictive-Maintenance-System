import React from "react";

export default function RiskPanel({ highRiskCount }) {
  return (
    <div className="card-panel">
      <h3>At-risk vehicles</h3>
      <p>{highRiskCount} vehicles with high risk score. Prioritize these for immediate intervention.</p>
    </div>
  );
}
