import React, { useState, useEffect, useRef } from 'react';
import {
  BrainCircuit, TrendingUp, AlertTriangle, ShieldCheck,
  Activity, Zap, Gauge, Thermometer, Droplets, RotateCcw,
  Send, Loader2, BarChart3, History, Cpu
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { getPrediction, getPredictionHistory, getPredictionStats, getModelInfo } from '../services/api';

// ─── Default / simulated sensor values ──────────────────
const DEFAULT_SENSORS = {
  engine_temp: 85,
  oil_pressure: 42,
  rpm: 2800,
  vibration: 0.35,
  battery_voltage: 12.6,
  mileage: 45000,
};

const SENSOR_META = [
  { key: 'engine_temp',     label: 'Engine Temp',     unit: '°C',  icon: Thermometer, min: 0, max: 250, step: 1,     danger: v => v > 100 },
  { key: 'oil_pressure',    label: 'Oil Pressure',    unit: 'psi', icon: Droplets,     min: 0, max: 80,  step: 1,     danger: v => v < 35 },
  { key: 'rpm',             label: 'Engine RPM',      unit: 'rpm', icon: Gauge,        min: 0, max: 8000, step: 50,   danger: v => v > 5000 },
  { key: 'vibration',       label: 'Vibration',       unit: 'g',   icon: Activity,     min: 0, max: 3,   step: 0.01,  danger: v => v > 0.7 },
  { key: 'battery_voltage', label: 'Battery Voltage', unit: 'V',   icon: Zap,          min: 8, max: 16,  step: 0.1,   danger: v => v < 11.5 },
  { key: 'mileage',         label: 'Mileage',         unit: 'km',  icon: RotateCcw,    min: 0, max: 500000, step: 1000, danger: v => v > 150000 },
];

const RISK_COLORS = { Low: '#059669', Medium: '#d97706', High: '#dc2626' };
const PIE_COLORS  = ['#059669', '#d97706', '#dc2626'];

// ─── Simulated live data presets ────────────────────────
const PRESETS = [
  { label: '🟢 Healthy Vehicle',   values: { engine_temp: 82, oil_pressure: 45, rpm: 2200, vibration: 0.25, battery_voltage: 13.1, mileage: 32000 } },
  { label: '🟡 Warning Signs',     values: { engine_temp: 98, oil_pressure: 36, rpm: 3800, vibration: 0.55, battery_voltage: 12.0, mileage: 85000 } },
  { label: '🔴 Critical Failure',  values: { engine_temp: 118, oil_pressure: 28, rpm: 4500, vibration: 0.95, battery_voltage: 11.2, mileage: 145000 } },
];

const PredictionsPage = () => {
  const [sensors, setSensors] = useState({ ...DEFAULT_SENSORS });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [activeTab, setActiveTab] = useState('predict'); // 'predict' | 'history' | 'insights'
  const [simulating, setSimulating] = useState(false);
  const simRef = useRef(null);

  // Load stats and model info on mount
  useEffect(() => {
    loadSidebarData();
  }, []);

  async function loadSidebarData() {
    const [statsData, modelData, historyData] = await Promise.all([
      getPredictionStats(168),
      getModelInfo(),
      getPredictionHistory({ limit: 20 }),
    ]);
    setStats(statsData);
    setModelInfo(modelData);
    setHistory(historyData);
  }

  // ─── Prediction handler ─────────────────────────────
  async function handlePredict() {
    setLoading(true);
    setError(null);
    try {
      const res = await getPrediction(sensors);
      setResult(res);
      // Refresh history
      const historyData = await getPredictionHistory({ limit: 20 });
      setHistory(historyData);
      const statsData = await getPredictionStats(168);
      setStats(statsData);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Prediction failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  // ─── Simulate live data ─────────────────────────────
  function toggleSimulation() {
    if (simulating) {
      clearInterval(simRef.current);
      setSimulating(false);
    } else {
      setSimulating(true);
      simRef.current = setInterval(async () => {
        const newSensors = {
          engine_temp:     +(75 + Math.random() * 55).toFixed(1),
          oil_pressure:    +(25 + Math.random() * 30).toFixed(1),
          rpm:             +(1500 + Math.random() * 4500).toFixed(0),
          vibration:       +(0.1 + Math.random() * 1.2).toFixed(2),
          battery_voltage: +(10.5 + Math.random() * 3.5).toFixed(1),
          mileage:         +(10000 + Math.random() * 200000).toFixed(0),
        };
        // Convert string values back to numbers
        const numericSensors = {};
        for (const k of Object.keys(newSensors)) numericSensors[k] = Number(newSensors[k]);
        setSensors(numericSensors);
        try {
          const res = await getPrediction(numericSensors);
          setResult(res);
        } catch { /* silently continue simulation */ }
      }, 3000);
    }
  }

  useEffect(() => {
    return () => { if (simRef.current) clearInterval(simRef.current); };
  }, []);

  // ─── Risk distribution pie data ─────────────────────
  const pieData = stats ? [
    { name: 'Low',    value: stats.low_risk_count },
    { name: 'Medium', value: stats.medium_risk_count },
    { name: 'High',   value: stats.high_risk_count },
  ] : [];

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="prediction-header-icon">
            <BrainCircuit size={28} />
          </div>
          <div>
            <h1 className="page-title">AI Predictive Maintenance</h1>
            <p className="page-subtitle">Real-time ML-powered failure prediction engine (XGBoost v4)</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`btn ${simulating ? 'btn-danger-solid' : 'btn-secondary'}`}
            onClick={toggleSimulation}
            id="simulation-toggle"
          >
            <Activity size={16} />
            {simulating ? 'Stop Simulation' : 'Live Simulation'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="prediction-tabs mb-4">
        {[
          { id: 'predict',  label: 'Predict',  icon: Cpu },
          { id: 'history',  label: 'History',  icon: History },
          { id: 'insights', label: 'Insights', icon: BarChart3 },
        ].map(tab => (
          <button
            key={tab.id}
            className={`prediction-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            id={`tab-${tab.id}`}
          >
            <tab.icon size={16} /> {tab.label}
          </button>
        ))}
      </div>

      {/* ═══════════ PREDICT TAB ═══════════ */}
      {activeTab === 'predict' && (
        <>
          {/* Quick Presets */}
          <div className="prediction-presets mb-4">
            {PRESETS.map((p, i) => (
              <button
                key={i}
                className="btn btn-secondary preset-btn"
                onClick={() => { setSensors({ ...p.values }); setResult(null); }}
                id={`preset-${i}`}
              >
                {p.label}
              </button>
            ))}
          </div>

          <div className="prediction-layout">
            {/* LEFT: Sensor Input Form */}
            <div className="card prediction-form-card">
              <div className="card-header">
                <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Gauge size={18} /> Sensor Readings
                </h3>
              </div>

              <div className="sensor-grid">
                {SENSOR_META.map(s => {
                  const val = sensors[s.key];
                  const isDanger = s.danger(val);
                  const Icon = s.icon;
                  return (
                    <div key={s.key} className={`sensor-input-group ${isDanger ? 'sensor-danger' : ''}`}>
                      <div className="sensor-input-header">
                        <div className="sensor-input-label">
                          <Icon size={14} />
                          <span>{s.label}</span>
                        </div>
                        <span className="sensor-input-value" style={{ color: isDanger ? 'var(--danger)' : 'var(--text-primary)' }}>
                          {val} {s.unit}
                        </span>
                      </div>
                      <input
                        type="range"
                        min={s.min}
                        max={s.max}
                        step={s.step}
                        value={val}
                        onChange={e => setSensors(prev => ({ ...prev, [s.key]: Number(e.target.value) }))}
                        className={`sensor-slider ${isDanger ? 'slider-danger' : ''}`}
                        id={`slider-${s.key}`}
                      />
                      <div className="sensor-range-labels">
                        <span>{s.min}</span>
                        <span>{s.max}</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <button
                className="btn btn-primary predict-btn"
                onClick={handlePredict}
                disabled={loading}
                id="predict-button"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                {loading ? 'Analyzing...' : 'Run Prediction'}
              </button>

              {error && (
                <div className="prediction-error">
                  <AlertTriangle size={16} /> {error}
                </div>
              )}
            </div>

            {/* RIGHT: Prediction Result */}
            <div className="prediction-result-area">
              {result ? (
                <>
                  {/* Main Result Card */}
                  <div className={`card prediction-result-card risk-${result.risk_level.toLowerCase()}`}>
                    <div className="result-header">
                      <div>
                        <span className="result-label">Failure Probability</span>
                        <div className="result-probability">
                          {(result.failure_probability * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div className={`risk-badge-large risk-${result.risk_level.toLowerCase()}`}>
                        {result.risk_level === 'High' ? <AlertTriangle size={20} /> :
                         result.risk_level === 'Medium' ? <Activity size={20} /> :
                         <ShieldCheck size={20} />}
                        {result.risk_level} Risk
                      </div>
                    </div>

                    {/* Probability Gauge */}
                    <div className="probability-gauge-container">
                      <div className="probability-gauge-track">
                        <div
                          className="probability-gauge-fill"
                          style={{
                            width: `${Math.min(result.failure_probability * 100, 100)}%`,
                            background: result.risk_level === 'High' ? 'linear-gradient(90deg, #d97706, #dc2626)' :
                                        result.risk_level === 'Medium' ? 'linear-gradient(90deg, #059669, #d97706)' :
                                        'linear-gradient(90deg, #059669, #10b981)',
                          }}
                        />
                      </div>
                      <div className="probability-gauge-labels">
                        <span>0%</span>
                        <span style={{ left: '25%' }}>25%</span>
                        <span style={{ left: '50%' }}>50%</span>
                        <span style={{ left: '75%' }}>75%</span>
                        <span>100%</span>
                      </div>
                    </div>

                    {/* Prediction outcome */}
                    <div className="result-outcome">
                      <div className={`outcome-badge ${result.prediction === 1 ? 'failure' : 'safe'}`}>
                        {result.prediction === 1 ? '⚠️ FAILURE PREDICTED' : '✅ SYSTEM NORMAL'}
                      </div>
                      <span className="text-muted text-xs">
                        Threshold: {(result.threshold_used * 100).toFixed(0)}% | Model: XGBoost v4
                      </span>
                    </div>

                    {/* Sensor Flags */}
                    {result.sensor_flags && result.sensor_flags.length > 0 && (
                      <div className="sensor-flags">
                        <span className="sensor-flags-title">⚡ Domain Rule Triggers:</span>
                        {result.sensor_flags.map((flag, i) => (
                          <span key={i} className="badge badge-danger">{flag}</span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Sensor Summary Cards */}
                  <div className="sensor-summary-grid">
                    {SENSOR_META.map(s => {
                      const val = sensors[s.key];
                      const isDanger = s.danger(val);
                      const Icon = s.icon;
                      return (
                        <div key={s.key} className={`sensor-summary-card ${isDanger ? 'sensor-danger' : ''}`}>
                          <Icon size={16} style={{ color: isDanger ? 'var(--danger)' : 'var(--text-secondary)' }} />
                          <div className="sensor-summary-value" style={{ color: isDanger ? 'var(--danger)' : 'var(--text-primary)' }}>
                            {val}
                          </div>
                          <div className="sensor-summary-label">{s.unit}</div>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <div className="card prediction-empty-state">
                  <BrainCircuit size={48} style={{ color: 'var(--text-secondary)', opacity: 0.4 }} />
                  <h3>Ready to Analyze</h3>
                  <p className="text-muted">Adjust sensor values and click "Run Prediction" to get real-time failure analysis from the ML model.</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* ═══════════ HISTORY TAB ═══════════ */}
      {activeTab === 'history' && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title"><History size={18} /> Prediction History</h3>
            <span className="text-muted text-xs">{history.length} records</span>
          </div>
          {history.length === 0 ? (
            <div className="prediction-empty-state" style={{ padding: '3rem' }}>
              <History size={40} style={{ color: 'var(--text-secondary)', opacity: 0.4 }} />
              <p className="text-muted">No predictions yet. Run a prediction to see history.</p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Engine °C</th>
                    <th>Oil PSI</th>
                    <th>RPM</th>
                    <th>Vibration</th>
                    <th>Battery V</th>
                    <th>Mileage</th>
                    <th>Probability</th>
                    <th>Risk</th>
                    <th>Prediction</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, i) => (
                    <tr key={h.id || i}>
                      <td className="text-muted text-xs">{new Date(h.created_at).toLocaleString()}</td>
                      <td>{h.engine_temp}</td>
                      <td>{h.oil_pressure}</td>
                      <td>{h.rpm}</td>
                      <td>{h.vibration}</td>
                      <td>{h.battery_voltage}</td>
                      <td>{Number(h.mileage).toLocaleString()}</td>
                      <td className="font-medium">{(h.failure_probability * 100).toFixed(1)}%</td>
                      <td>
                        <span className={`badge badge-${h.risk_level === 'High' ? 'danger' : h.risk_level === 'Medium' ? 'warning' : 'success'}`}>
                          {h.risk_level}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${h.prediction === 1 ? 'badge-danger' : 'badge-success'}`}>
                          {h.prediction === 1 ? 'Failure' : 'Normal'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ═══════════ INSIGHTS TAB ═══════════ */}
      {activeTab === 'insights' && (
        <div className="prediction-insights-layout">
          {/* Stats Cards */}
          <div className="grid-cols-4 mb-4">
            <div className="card stat-card" style={{ borderTop: '4px solid var(--primary)' }}>
              <div className="stat-title">Total Predictions</div>
              <div className="stat-value">{stats?.total_predictions ?? 0}</div>
              <div className="stat-trend neutral">Last 7 days</div>
            </div>
            <div className="card stat-card" style={{ borderTop: '4px solid var(--danger)' }}>
              <div className="stat-title">High Risk</div>
              <div className="stat-value text-danger">{stats?.high_risk_count ?? 0}</div>
              <div className="stat-trend down">Require attention</div>
            </div>
            <div className="card stat-card" style={{ borderTop: '4px solid var(--warning)' }}>
              <div className="stat-title">Avg Failure Probability</div>
              <div className="stat-value">{((stats?.avg_failure_probability ?? 0) * 100).toFixed(1)}%</div>
              <div className="stat-trend neutral">Across all predictions</div>
            </div>
            <div className="card stat-card" style={{ borderTop: '4px solid var(--success)' }}>
              <div className="stat-title">Failure Rate</div>
              <div className="stat-value">{((stats?.recent_failure_rate ?? 0) * 100).toFixed(1)}%</div>
              <div className="stat-trend up">Predictions flagged failure</div>
            </div>
          </div>

          <div className="grid-cols-2 mb-4">
            {/* Risk Distribution Pie */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Risk Distribution</h3>
              </div>
              <div className="chart-container" style={{ height: '280px' }}>
                {pieData.some(d => d.value > 0) ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {pieData.map((_, idx) => (
                          <Cell key={idx} fill={PIE_COLORS[idx]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="prediction-empty-state">
                    <p className="text-muted">Run predictions to see distribution</p>
                  </div>
                )}
              </div>
            </div>

            {/* Model Info */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title"><Cpu size={18} /> Model Information</h3>
              </div>
              {modelInfo ? (
                <div className="model-info-grid">
                  <div className="model-info-row">
                    <span className="text-muted">Version</span>
                    <span className="font-medium">{modelInfo.model_version}</span>
                  </div>
                  <div className="model-info-row">
                    <span className="text-muted">Threshold</span>
                    <span className="font-medium">{(modelInfo.threshold * 100).toFixed(0)}%</span>
                  </div>
                  <div className="model-info-row">
                    <span className="text-muted">Domain Rules</span>
                    <span className={`badge ${modelInfo.domain_rules_active ? 'badge-success' : 'badge-neutral'}`}>
                      {modelInfo.domain_rules_active ? 'Active' : 'Disabled'}
                    </span>
                  </div>
                  {modelInfo.training_metrics && (
                    <>
                      <div className="model-info-row">
                        <span className="text-muted">Accuracy</span>
                        <span className="font-medium">{(modelInfo.training_metrics.accuracy * 100).toFixed(1)}%</span>
                      </div>
                      <div className="model-info-row">
                        <span className="text-muted">Precision</span>
                        <span className="font-medium">{(modelInfo.training_metrics.precision * 100).toFixed(1)}%</span>
                      </div>
                      <div className="model-info-row">
                        <span className="text-muted">Recall</span>
                        <span className="font-medium">{(modelInfo.training_metrics.recall * 100).toFixed(1)}%</span>
                      </div>
                      <div className="model-info-row">
                        <span className="text-muted">F1 Score</span>
                        <span className="font-medium">{(modelInfo.training_metrics.f1 * 100).toFixed(1)}%</span>
                      </div>
                    </>
                  )}
                  <div className="model-info-row">
                    <span className="text-muted">Features</span>
                    <span className="text-xs">{modelInfo.feature_order?.join(', ')}</span>
                  </div>
                </div>
              ) : (
                <div className="prediction-empty-state">
                  <p className="text-muted">Model info unavailable — ensure backend is running</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionsPage;
