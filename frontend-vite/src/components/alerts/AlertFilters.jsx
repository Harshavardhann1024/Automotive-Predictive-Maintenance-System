import React from "react";

export default function AlertFilters({ severity, status, setSeverity, setStatus }) {
  return (
    <div className="filters-row">
      <label>
        Severity
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option>All</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </label>
      <label>
        Status
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option>All</option>
          <option value="Active">Active</option>
          <option value="Acknowledged">Acknowledged</option>
          <option value="Resolved">Resolved</option>
        </select>
      </label>
    </div>
  );
}
