import React from "react";

export default function RecommendationPanel({ recommendations }) {
  return (
    <div className="card-panel">
      <h3>Health recommendations</h3>
      <ul>
        {recommendations.map((item) => (
          <li key={item.id}>{item.title} <small>({item.due})</small></li>
        ))}
      </ul>
    </div>
  );
}
