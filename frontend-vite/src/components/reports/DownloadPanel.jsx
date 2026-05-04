import React from "react";

export default function DownloadPanel() {
  return (
    <div className="card-panel">
      <h3>Quick download</h3>
      <ul>
        <li>Fleet performance summary</li>
        <li>Alerts data export</li>
        <li>Service operation report</li>
      </ul>
      <button className="button-primary">Generate report pack</button>
    </div>
  );
}
