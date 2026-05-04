import React from "react";

export default function ServiceSchedule({ tasks }) {
  return (
    <div className="card-panel">
      <h3>Service Schedule</h3>
      <ul>
        {tasks.map((task) => (
          <li key={task.id}>{task.vehicle}: {task.type} ({task.priority})</li>
        ))}
      </ul>
    </div>
  );
}
