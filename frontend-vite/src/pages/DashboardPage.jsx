import React, { useState, useEffect } from 'react';
import { 
  Car, AlertCircle, Activity, AlertTriangle, 
  ArrowUpRight, ArrowDownRight, TrendingUp, Loader2,
  BrainCircuit, ShieldCheck, Zap
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { fetchDashboardSummary, fetchAlerts, getChartData, downloadDashboardReport, getPredictionStats, getPrediction } from '../services/api';
import { apiClient } from '../services/authApi';

const RISK_COLORS = ['#059669', '#d97706', '#dc2626'];

const DashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardKPIs, setDashboardKPIs] = useState(null);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [chartData, setChartData] = useState({ fleetHealthTrend: [], failRiskTrend: [] });
  const [predStats, setPredStats] = useState(null);
  const [liveResult, setLiveResult] = useState(null);
  const [liveLoading, setLiveLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [kpis, alerts, charts, stats] = await Promise.all([
          fetchDashboardSummary(),
          fetchAlerts(),
          Promise.resolve(getChartData()),
          getPredictionStats(168),
        ]);
        setDashboardKPIs(kpis);
        setRecentAlerts(alerts);
        setChartData({
          fleetHealthTrend: charts?.fleetHealth || charts?.fleetHealthTrend || [],
          failRiskTrend: charts?.riskTrend || charts?.failRiskTrend || []
        });
        setPredStats(stats);
      } catch (e) {
        console.error("Error loading dashboard", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Quick live prediction from dashboard
  async function runQuickPrediction() {
    setLiveLoading(true);
    try {
      const res = await getPrediction({
        engine_temp: 95 + Math.random() * 30,
        oil_pressure: 28 + Math.random() * 20,
        rpm: 2500 + Math.random() * 3000,
        vibration: 0.2 + Math.random() * 0.9,
        battery_voltage: 11 + Math.random() * 3,
        mileage: 40000 + Math.random() * 120000,
      });
      setLiveResult(res);
      // Refresh stats
      const stats = await getPredictionStats(168);
      setPredStats(stats);
    } catch (err) {
      console.error("Quick prediction failed", err);
    } finally {
      setLiveLoading(false);
    }
  }

  if (loading || !dashboardKPIs) {
    return (
      <div style={{ padding: '4rem', display: 'flex', justifyContent: 'center' }}>
        <Loader2 className="animate-spin text-primary" size={32} />
      </div>
    );
  }

  // Risk distribution pie data
  const riskPieData = predStats ? [
    { name: 'Low', value: predStats.low_risk_count || 0 },
    { name: 'Medium', value: predStats.medium_risk_count || 0 },
    { name: 'High', value: predStats.high_risk_count || 0 },
  ] : [];
  const hasRiskData = riskPieData.some(d => d.value > 0);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Executive Dashboard</h1>
          <p className="page-subtitle">Real-time overview of fleet operations and health</p>
        </div>
        <button className="btn btn-primary" disabled={loading} onClick={async () => {
          try {
            await downloadDashboardReport();
            alert('Executive Dashboard Report successfully generated and downloaded!');
          } catch(err) { alert('Error generating report'); }
        }}>
          <TrendingUp size={16} /> Generate Report
        </button>
      </div>

      {/* KPIs */}
      <div className="grid-cols-4 mb-4">
        <div className="card stat-card">
          <div className="stat-header">
            <span className="stat-title">Total Vehicles</span>
            <div className="stat-icon primary"><Car size={20} /></div>
          </div>
          <div className="stat-value">{(dashboardKPIs?.total_vehicles || dashboardKPIs?.totalVehicles || 0).toLocaleString()}</div>
          <div className="stat-trend up"><ArrowUpRight size={14} /> +2.4% from last month</div>
        </div>
        
        <div className="card stat-card">
          <div className="stat-header">
            <span className="stat-title">Active Alerts</span>
            <div className="stat-icon warning"><AlertCircle size={20} /></div>
          </div>
          <div className="stat-value">{dashboardKPIs?.active_alerts ?? dashboardKPIs?.activeAlerts ?? 0}</div>
          <div className="stat-trend down"><ArrowDownRight size={14} /> -12% from last week</div>
        </div>

        <div className="card stat-card">
          <div className="stat-header">
            <span className="stat-title">Avg Fleet Health</span>
            <div className="stat-icon success"><Activity size={20} /></div>
          </div>
          <div className="stat-value">{dashboardKPIs?.average_health ?? dashboardKPIs?.avgFleetHealth ?? 0}/100</div>
          <div className="stat-trend up"><ArrowUpRight size={14} /> Stable</div>
        </div>

        <div className="card stat-card">
          <div className="stat-header">
            <span className="stat-title">High Risk Vehicles</span>
            <div className="stat-icon danger"><AlertTriangle size={20} /></div>
          </div>
          <div className="stat-value">{dashboardKPIs?.high_risk_vehicles ?? dashboardKPIs?.highRiskVehicles ?? 0}</div>
          <div className="stat-trend neutral">Needs immediate attention</div>
        </div>
      </div>

      {/* ML Prediction Stats Row */}
      <div className="grid-cols-4 mb-4">
        <div className="card stat-card" style={{ borderTop: '4px solid var(--purple)' }}>
          <div className="stat-header">
            <span className="stat-title">ML Predictions (7d)</span>
            <div className="stat-icon" style={{ backgroundColor: 'var(--purple-light)', color: 'var(--purple)' }}>
              <BrainCircuit size={20} />
            </div>
          </div>
          <div className="stat-value">{predStats?.total_predictions ?? 0}</div>
          <div className="stat-trend neutral">XGBoost v4 engine</div>
        </div>

        <div className="card stat-card" style={{ borderTop: '4px solid var(--danger)' }}>
          <div className="stat-header">
            <span className="stat-title">High Risk Predictions</span>
            <div className="stat-icon danger"><AlertTriangle size={20} /></div>
          </div>
          <div className="stat-value text-danger">{predStats?.high_risk_count ?? 0}</div>
          <div className="stat-trend down">Require immediate action</div>
        </div>

        <div className="card stat-card" style={{ borderTop: '4px solid var(--warning)' }}>
          <div className="stat-header">
            <span className="stat-title">Avg Failure Probability</span>
            <div className="stat-icon warning"><Activity size={20} /></div>
          </div>
          <div className="stat-value">{((predStats?.avg_failure_probability ?? 0) * 100).toFixed(1)}%</div>
          <div className="stat-trend neutral">Across all predictions</div>
        </div>

        <div className="card stat-card" style={{ borderTop: '4px solid var(--success)' }}>
          <div className="stat-header">
            <span className="stat-title">Detection Rate</span>
            <div className="stat-icon success"><ShieldCheck size={20} /></div>
          </div>
          <div className="stat-value">{((predStats?.recent_failure_rate ?? 0) * 100).toFixed(1)}%</div>
          <div className="stat-trend up">Failures detected</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid-cols-2 mb-4">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Fleet Health Trend</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData.fleetHealthTrend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--success)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--success)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                <XAxis dataKey="day" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} domain={[60, 100]} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: '1px solid var(--border)', boxShadow: 'var(--shadow-md)' }}
                />
                <Area type="monotone" dataKey="score" stroke="var(--success)" strokeWidth={3} fillOpacity={1} fill="url(#colorHealth)" />
                <Line type="monotone" dataKey="threshold" stroke="var(--danger)" strokeDasharray="5 5" strokeWidth={1} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Chart (ML) */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BrainCircuit size={18} /> ML Risk Distribution
            </h3>
            <button className="btn btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }} onClick={runQuickPrediction} disabled={liveLoading}>
              {liveLoading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
              Quick Predict
            </button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="chart-container" style={{ flex: 1 }}>
              {hasRiskData ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {riskPieData.map((_, idx) => (
                        <Cell key={idx} fill={RISK_COLORS[idx]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '0.5rem' }}>
                  <BrainCircuit size={36} style={{ color: 'var(--text-secondary)', opacity: 0.3 }} />
                  <p className="text-muted text-xs">Run predictions to visualize distribution</p>
                </div>
              )}
            </div>

            {/* Live result mini-card */}
            {liveResult && (
              <div className={`card live-result-mini risk-border-${liveResult.risk_level.toLowerCase()}`} style={{ minWidth: '160px', padding: '1rem' }}>
                <div className="text-xs text-muted" style={{ marginBottom: '0.25rem' }}>Latest Prediction</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: liveResult.risk_level === 'High' ? 'var(--danger)' : liveResult.risk_level === 'Medium' ? 'var(--warning)' : 'var(--success)' }}>
                  {(liveResult.failure_probability * 100).toFixed(1)}%
                </div>
                <span className={`badge badge-${liveResult.risk_level === 'High' ? 'danger' : liveResult.risk_level === 'Medium' ? 'warning' : 'success'}`} style={{ marginTop: '0.5rem' }}>
                  {liveResult.risk_level} Risk
                </span>
                <div className={`outcome-badge-mini ${liveResult.prediction === 1 ? 'failure' : 'safe'}`} style={{ marginTop: '0.5rem' }}>
                  {liveResult.prediction === 1 ? '⚠️ Failure' : '✅ Normal'}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Failure Risk Forecast */}
      <div className="grid-cols-2 mb-4">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Failure Risk Forecast</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData.failRiskTrend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                <XAxis dataKey="day" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: '1px solid var(--border)', boxShadow: 'var(--shadow-md)' }}
                />
                <Line type="monotone" dataKey="highRisk" stroke="var(--danger)" strokeWidth={3} dot={{ strokeWidth: 2, r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Real-time Failure Alerts from ML */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={18} style={{ color: 'var(--danger)' }} /> Real-time ML Alerts
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {predStats && predStats.high_risk_count > 0 ? (
              <>
                <div className="ml-alert-card ml-alert-critical">
                  <div className="ml-alert-icon"><AlertTriangle size={18} /></div>
                  <div>
                    <div className="ml-alert-title">{predStats.high_risk_count} High-Risk Prediction{predStats.high_risk_count > 1 ? 's' : ''}</div>
                    <div className="ml-alert-desc">Failure probability exceeds 50% threshold</div>
                  </div>
                </div>
                {predStats.medium_risk_count > 0 && (
                  <div className="ml-alert-card ml-alert-warning">
                    <div className="ml-alert-icon"><Activity size={18} /></div>
                    <div>
                      <div className="ml-alert-title">{predStats.medium_risk_count} Medium-Risk Prediction{predStats.medium_risk_count > 1 ? 's' : ''}</div>
                      <div className="ml-alert-desc">Probability between 25%–50%, monitoring recommended</div>
                    </div>
                  </div>
                )}
                <div className="ml-alert-card ml-alert-info">
                  <div className="ml-alert-icon"><ShieldCheck size={18} /></div>
                  <div>
                    <div className="ml-alert-title">{predStats.low_risk_count} Low-Risk Prediction{predStats.low_risk_count > 1 ? 's' : ''}</div>
                    <div className="ml-alert-desc">Systems operating within normal parameters</div>
                  </div>
                </div>
              </>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', gap: '0.5rem' }}>
                <ShieldCheck size={36} style={{ color: 'var(--success)', opacity: 0.5 }} />
                <p className="text-muted">No high-risk predictions detected</p>
                <p className="text-xs text-muted">Use the Predictions page to analyze sensor data</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Alerts Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Critical Alerts</h3>
          <span className="card-action text-xs font-medium">View All</span>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Vehicle</th>
                <th>Issue Type</th>
                <th>Severity</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentAlerts.map(alert => (
                <tr key={alert.id}>
                  <td className="font-medium">{alert.id}</td>
                  <td>{alert.vehicle_id || alert.vehicle || 'Unknown'}</td>
                  <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{alert.message || alert.type || 'Alert details'}</td>
                  <td>
                    <span className={`badge badge-${alert.severity === 'Critical' ? 'danger' : alert.severity === 'High' ? 'warning' : alert.severity === 'Medium' ? 'info' : 'success'}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="text-muted text-sm">{alert.created_at ? new Date(alert.created_at).toLocaleString() : alert.time || 'N/A'}</td>
                  <td>
                    <span className={`badge badge-${alert.status === 'Open' || alert.status === 'Active' ? 'danger' : alert.status === 'In Progress' ? 'warning' : 'neutral'}`}>
                      {alert.status}
                    </span>
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

export default DashboardPage;
