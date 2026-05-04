import React from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

export default function RiskChart({ data }) {
  return (
    <article className="chart-card">
      <h3>High-Risk Vehicles Trend</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="day" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Area type="monotone" dataKey="highRisk" stroke="#dc2626" fill="#fda4af" fillOpacity={0.4} />
        </AreaChart>
      </ResponsiveContainer>
    </article>
  );
}
