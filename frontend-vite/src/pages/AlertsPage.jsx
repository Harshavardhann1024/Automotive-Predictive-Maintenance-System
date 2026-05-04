import React, { useState, useEffect } from 'react';
import { fetchAlerts, resolveAlert } from '../services/api';
import { Filter, Search, CheckCircle, Clock, Loader2 } from 'lucide-react';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchAlerts();
        setAlerts(data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleResolve = async (id) => {
    setResolving(id);
    await resolveAlert(id);
    setAlerts(alerts.map(a => a.id === id ? { ...a, status: 'Resolved' } : a));
    setResolving(null);
  };

  const filteredAlerts = alerts.filter(a => {
    if (!searchTerm) return true;
    const s = searchTerm.toLowerCase();
    const idStr = a.id || '';
    const vStr = a.vehicle || a.vehicle_id || '';
    const descStr = a.type || a.message || a.msg || '';
    const sevStr = a.severity || '';
    return idStr.toLowerCase().includes(s) || 
           vStr.toLowerCase().includes(s) || 
           descStr.toLowerCase().includes(s) || 
           sevStr.toLowerCase().includes(s);
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Operational Alerts</h1>
          <p className="page-subtitle">Real-time alerts and anomalies across the fleet</p>
        </div>
      </div>

      <div className="grid-cols-4 mb-4">
        <div className="card stat-card">
          <div className="stat-value text-danger">24</div>
          <div className="stat-title">Critical Severity</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value text-warning">86</div>
          <div className="stat-title">High & Medium</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value text-success">32</div>
          <div className="stat-title">Resolved Today</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">1.4h</div>
          <div className="stat-title">Avg Time to Resolve</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="header-search" style={{ margin: 0, backgroundColor: 'var(--bg-main)', border: '1px solid var(--border)' }}>
            <Search size={16} />
            <input 
              type="text" 
              placeholder="Search by vehicle, message, or severity..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Vehicle & Model</th>
                <th>Issue Description</th>
                <th>Severity</th>
                <th>Triggered At</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '3rem' }}>
                    <Loader2 className="animate-spin text-primary mx-auto" size={32} />
                  </td>
                </tr>
              ) : filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-4 text-muted">No alerts found matching search.</td>
                </tr>
              ) : filteredAlerts.map(alert => (
                <tr key={alert.id}>
                  <td className="font-medium text-primary">{alert.id}</td>
                  <td className="font-medium">{alert.vehicle || alert.vehicle_id}</td>
                  <td>{alert.type || alert.message || alert.msg}</td>
                  <td>
                    <span className={`badge badge-${alert.severity === 'Critical' ? 'danger' : alert.severity === 'High' ? 'warning' : alert.severity === 'Medium' ? 'info' : 'success'}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Clock size={14} /> {alert.time || alert.created_at ? new Date(alert.created_at).toLocaleString() : 'N/A'}
                  </td>
                  <td>
                    <span className={`badge badge-${alert.status === 'Open' ? 'danger' : alert.status === 'In Progress' ? 'warning' : 'neutral'}`}>
                      {alert.status || alert.state}
                    </span>
                  </td>
                  <td>
                    {(alert.status !== 'Resolved' && alert.state !== 'Resolved') && (
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => handleResolve(alert.id)}
                        disabled={resolving === alert.id}
                      >
                        {resolving === alert.id ? <Loader2 size={14} className="animate-spin" /> : <><CheckCircle size={14} /> Resolve</>}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
