import React from "react";
import { Link } from "react-router-dom";
import Badge from "../common/Badge";

export default function VehicleCard({ vehicle }) {
  return (
    <article className="vehicle-card">
      <div className="vehicle-top">
        <h3>{vehicle.name}</h3>
        <Badge>{vehicle.risk_level}</Badge>
      </div>
      <p className="vehicle-meta">{vehicle.model} • {vehicle.registration_number}</p>
      <div className="vehicle-stats">
        <div>
          <strong>{vehicle.health_score}%</strong>
          <small>Health</small>
        </div>
        <div>
          <strong>{vehicle.mileage.toLocaleString()} km</strong>
          <small>Mileage</small>
        </div>
        <div>
          <strong>{vehicle.alerts_count}</strong>
          <small>Alerts</small>
        </div>
      </div>
      <div className="vehicle-footer">
        <Link to={`/vehicles/${vehicle.id}`}>View details</Link>
      </div>
    </article>
  );
}
