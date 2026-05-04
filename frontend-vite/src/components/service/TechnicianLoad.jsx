import React from "react";

export default function TechnicianLoad({ load }) {
  return (
    <div className="card-panel">
      <h3>Technician Load</h3>
      <ul>
        {load.map((item) => (
          <li key={item.name}>{item.name}: {item.jobs} jobs</li>
        ))}
      </ul>
    </div>
  );
}
