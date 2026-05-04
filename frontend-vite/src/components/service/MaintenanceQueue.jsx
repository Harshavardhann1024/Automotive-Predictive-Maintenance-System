import React from "react";

export default function MaintenanceQueue({ tasks }) {
  return (
    <div className="card-panel">
      <h3>Maintenance Queue</h3>
      <ul>
        {tasks.map((task) => (
          <li key={task.id}>{task.vehicle} | {task.assigned_to} | {task.eta}</li>
        ))}
      </ul>
    </div>
  );
}
