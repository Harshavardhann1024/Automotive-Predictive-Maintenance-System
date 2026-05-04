import React from "react";

export default function EmptyState({ title = "Nothing found", description = "No content available yet." }) {
  return (
    <div className="empty-state-panel">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}
