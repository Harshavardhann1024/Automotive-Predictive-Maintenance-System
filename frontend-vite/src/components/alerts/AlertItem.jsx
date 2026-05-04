import React from "react";
import Badge from "../common/Badge";

export default function AlertItem({ alert }) {
  return (
    <div className="alert-card">
      <div className="alert-card-left">
        <h4>{alert.message}</h4>
        <p>{alert.vehicle_id} • {new Date(alert.created_at).toLocaleString()}</p>
      </div>
      <div className="alert-card-right">
        <Badge>{alert.severity}</Badge>
        <Badge>{alert.status}</Badge>
      </div>
    </div>
  );
}
