import React from "react";
import { HeartPulse } from "lucide-react";

export default function HealthSummary({ summary }) {
  const health = summary?.average_health ?? 0;
  return (
    <section className="health-summary">
      <div className="health-summary-left">
        <h2>Fleet Health Summary</h2>
        <p>Overall fleet status based on sensor fusion and model judgement.</p>
      </div>
      <div className="health-summary-right">
        <div className="health-score">
          <HeartPulse size={22} />
          <span>{health}%</span>
        </div>
        <div>Average health score</div>
      </div>
    </section>
  );
}
