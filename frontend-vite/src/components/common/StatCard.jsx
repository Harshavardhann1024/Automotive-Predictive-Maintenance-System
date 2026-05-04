import React from "react";

export default function StatCard({ label, value, icon, growth }) {
  return (
    <article className="stat-card" aria-label={label}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
      {growth !== undefined && (
        <div className={`stat-growth ${growth >= 0 ? "positive" : "negative"}`}>
          {growth >= 0 ? `+${growth}%` : `${growth}%`}
        </div>
      )}
    </article>
  );
}
