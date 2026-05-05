import React, { useState } from 'react';
import { FileText, Download, FileBarChart, Calendar, TrendingUp, AlertTriangle, Wrench, Factory, Activity, Loader2, Search } from 'lucide-react';
import { generateReport, exportDataZip } from '../services/api';

export const ReportsPage = () => {
  const [downloading, setDownloading] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="page-subtitle">Export data and generate compliance reports</p>
        </div>
        <button className="btn btn-primary" disabled={downloading === 'zip'} onClick={async () => {
          setDownloading('zip');
          try {
            await exportDataZip();
            alert('Exported all data to ZIP archive successfully!');
          } catch { alert('Error exporting ZIP'); }
          setDownloading(null);
        }}>
          {downloading === 'zip' ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />} 
          Export All Data
        </button>
      </div>

      <div className="card mb-4" style={{ padding: '1rem 1.5rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div className="header-search" style={{ margin: 0, flex: 1, backgroundColor: 'white', border: '1px solid var(--border)' }}>
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Search reports by title or description..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="grid-cols-3">
        {[
          { title: 'Monthly Fleet Health', desc: 'Comprehensive overview of entire fleet status vs targets.', icon: <FileBarChart size={24} />, color: 'var(--primary)' },
          { title: 'Predictive Maintenance ROI', desc: 'Cost savings derived from early anomaly detection.', icon: <TrendingUp size={24} />, color: 'var(--success)' },
          { title: 'Critical Alert History', desc: 'Log of all severe anomalies and resolution times.', icon: <AlertTriangle size={24} />, color: 'var(--danger)' },
          { title: 'Technician Performance', desc: 'Service bay times, throughput, and efficiency scores.', icon: <Wrench size={24} />, color: 'var(--warning)' },
          { title: 'OEM Defect Compliance', desc: 'Detailed breakdown of manufacturer-level batch issues.', icon: <Factory size={24} />, color: 'var(--purple)' },
          { title: 'Carbon Emissions', desc: 'Estimated fleet emissions based on health and telemetry.', icon: <Activity size={24} />, color: 'var(--info)' },
        ]
        .filter(report => !searchTerm || report.title.toLowerCase().includes(searchTerm.toLowerCase()) || report.desc.toLowerCase().includes(searchTerm.toLowerCase()))
        .map((report, idx) => (
          <div key={idx} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ padding: '0.75rem', backgroundColor: `${report.color}20`, color: report.color, borderRadius: 'var(--radius-md)' }}>
                {report.icon}
              </div>
              <h3 className="card-title" style={{ marginBottom: 0 }}>{report.title}</h3>
            </div>
            <p className="text-secondary text-sm flex-1">{report.desc}</p>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto' }}>
              <button className="btn btn-primary flex-1" disabled={downloading === report.title + 'pdf'} onClick={async () => {
                setDownloading(report.title + 'pdf');
                try {
                  await generateReport('pdf', report.title);
                  alert(`Generated PDF for ${report.title}`);
                } catch { alert('Error generating report'); }
                setDownloading(null);
              }}>
                {downloading === report.title + 'pdf' ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />} PDF
              </button>
              <button className="btn btn-secondary flex-1" disabled={downloading === report.title + 'csv'} onClick={async () => {
                setDownloading(report.title + 'csv');
                try {
                  await generateReport('csv', report.title);
                  alert(`Generated CSV for ${report.title}`);
                } catch { alert('Error generating report'); }
                setDownloading(null);
              }}>
                {downloading === report.title + 'csv' ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />} CSV
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};



