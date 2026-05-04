import React from "react";
import Badge from "../common/Badge";

export default function PredictionCard({ prediction }) {
  return (
    <div className="prediction-card">
      <h4>{prediction.name}</h4>
      <p>Failure probability: <strong>{prediction.failure_probability}%</strong></p>
      <Badge>{prediction.suggested_action}</Badge>
      <p>Next service due: {prediction.next_service_due}</p>
    </div>
  );
}
