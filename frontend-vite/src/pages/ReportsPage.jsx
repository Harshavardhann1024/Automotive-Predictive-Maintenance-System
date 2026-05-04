import React from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import SectionHeader from "../components/common/SectionHeader";

const reports = [
  { id: "r1", title: "Fleet Health Report", generated: "2026-03-24", status: "Ready" },
  { id: "r2", title: "Alerts Trend Summary", generated: "2026-03-23", status: "Ready" },
  { id: "r3", title: "Service Center Ops", generated: "2026-03-22", status: "Processing" },
  { id: "r4", title: "Manufacturing Defect Radar", generated: "2026-03-21", status: "Ready" }
];

export default function ReportsPage() {
  return (
    <DashboardLayout title="Reports">
      <SectionHeader title="Reports & exports" subtitle="Download and share analytics reports for stakeholders" />

      <div className="card-grid">
        {reports.map((report) => (
          <section key={report.id} className="card-panel">
            <h3>{report.title}</h3>
            <p>Generated: {report.generated}</p>
            <p>Status: {report.status}</p>
            <button className="button-primary">Download PDF</button>
          </section>
        ))}
      </div>

      <section className="card-panel">
        <h3>Report overview</h3>
        <p>Each report is based on current fleet diagnostics and predictive model outputs. Combine reports with automated alerts for better executive review.</p>
      </section>
    </DashboardLayout>
  );
}
