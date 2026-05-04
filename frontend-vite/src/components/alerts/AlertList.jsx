import React from "react";
import AlertItem from "./AlertItem";

export default function AlertList({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <div className="empty-state-panel">No alerts detected.</div>;
  }

  return (
    <div className="alert-list">
      {alerts.map((alert) => <AlertItem key={alert.id} alert={alert} />)}
    </div>
  );
}
