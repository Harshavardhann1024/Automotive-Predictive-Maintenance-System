import React from "react";
import DashboardLayout from "../components/layout/DashboardLayout";

export default function SettingsPage() {
  return (
    <DashboardLayout title="Settings">
      <section className="settings-page">
        <h2>Settings</h2>
        <p>Configure user preferences, notifications, and integrations for your fleet tracking solution.</p>
        <div className="settings-card">
          <h3>Coming soon</h3>
          <p>This page is placeholder for future configuration options including user management, API keys, alert rules and data export.</p>
        </div>
      </section>
    </DashboardLayout>
  );
}
