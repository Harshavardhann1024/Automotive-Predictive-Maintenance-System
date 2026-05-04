import React from "react";

export default function RootCausePanel({ rootCauses }) {
  return (
    <div className="card-panel">
      <h3>Root cause hypotheses</h3>
      <ul>
        {rootCauses.map((cause) => (
          <li key={cause.id}>{cause.text}</li>
        ))}
      </ul>
    </div>
  );
}
