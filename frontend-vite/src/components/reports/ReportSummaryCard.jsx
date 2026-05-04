import React from "react";

export default function ReportSummaryCard({ report }) {
  return (
    <div className="report-card">
      <h4>{report.title}</h4>
      <p>Type: {report.type}</p>
      <p>Generated: {report.generated_on}</p>
      <p>Status: {report.status}</p>
      <button className="button-secondary">Download</button>
    </div>
  );
}
