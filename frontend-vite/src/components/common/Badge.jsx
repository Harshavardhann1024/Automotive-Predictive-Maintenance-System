import React from "react";

const statusColors = {
  Active: "green",
  "In Maintenance": "blue",
  Resolved: "gray",
  Acknowledged: "amber",
  Critical: "red",
  High: "orange",
  Medium: "yellow",
  Low: "teal",
  Unknown: "slate"
};

export default function Badge({ children, type = "default" }) {
  const color = statusColors[children] || statusColors[type] || "slate";
  return <span className={`badge badge-${color}`}>{children}</span>;
}
