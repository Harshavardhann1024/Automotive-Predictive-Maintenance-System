import React from "react";

export default function BatchImpactCard({ batch }) {
  return (
    <div className="card-panel">
      <h3>{batch.label}</h3>
      <p>Vehicles impacted: {batch.vehicles_impacted}</p>
      <p>Issue: {batch.issue}</p>
    </div>
  );
}
