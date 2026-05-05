/**
 * PredictionExplanationCard — SHAP Explainability Visualization
 * =============================================================
 * Displays the top contributing features to a failure prediction
 * with a horizontal bar chart (Recharts) and natural language summary.
 *
 * Props:
 *   - explanations: Array<{ feature, impact, value }>
 *   - naturalExplanation: string
 *   - riskLevel: "Low" | "Medium" | "High"
 *   - suppressedByRules: boolean
 *   - suppressionNote: string | null
 *   - shapBaseValue: number | null
 */

import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import { BrainCircuit, Info, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

// ─── Feature display labels ─────────────────────────────
const FEATURE_DISPLAY = {
  engine_temp: 'Engine Temp',
  oil_pressure: 'Oil Pressure',
  rpm: 'Engine RPM',
  vibration: 'Vibration',
  battery_voltage: 'Battery V',
  mileage: 'Mileage',
};

const FEATURE_UNITS = {
  engine_temp: '°C',
  oil_pressure: 'psi',
  rpm: 'rpm',
  vibration: 'g',
  battery_voltage: 'V',
  mileage: 'km',
};

// ─── Custom Tooltip ──────────────────────────────────────
const SHAPTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  const isPositive = data.impact > 0;
  return (
    <div className="shap-tooltip">
      <div className="shap-tooltip-header">
        <span className={`shap-indicator ${isPositive ? 'negative' : 'positive'}`}>
          {isPositive ? '🔴' : '🟢'}
        </span>
        <strong>{FEATURE_DISPLAY[data.feature] || data.feature}</strong>
      </div>
      <div className="shap-tooltip-body">
        <div>
          Value: <strong>{data.value} {FEATURE_UNITS[data.feature] || ''}</strong>
        </div>
        <div>
          Impact: <strong style={{ color: isPositive ? '#dc2626' : '#059669' }}>
            {isPositive ? '+' : ''}{data.impact.toFixed(4)}
          </strong>
        </div>
        <div className="shap-tooltip-desc">
          {isPositive
            ? 'Increases failure risk'
            : 'Reduces failure risk'}
        </div>
      </div>
    </div>
  );
};

const PredictionExplanationCard = ({
  explanations = [],
  naturalExplanation = '',
  riskLevel = 'Low',
  suppressedByRules = false,
  suppressionNote = null,
}) => {
  const [expanded, setExpanded] = useState(true);

  if (!explanations || explanations.length === 0) return null;

  // Take top 5 features by absolute impact for the chart
  const chartData = explanations
    .slice(0, 5)
    .map(e => ({
      ...e,
      label: FEATURE_DISPLAY[e.feature] || e.feature,
      absImpact: Math.abs(e.impact),
      fill: e.impact > 0 ? '#dc2626' : '#059669',
    }));

  // Determine header gradient based on risk level
  const headerGradient = riskLevel === 'High'
    ? 'linear-gradient(135deg, #fef2f2, #fee2e2)'
    : riskLevel === 'Medium'
      ? 'linear-gradient(135deg, #fffbeb, #fef3c7)'
      : 'linear-gradient(135deg, #ecfdf5, #d1fae5)';

  const accentColor = riskLevel === 'High'
    ? '#dc2626'
    : riskLevel === 'Medium'
      ? '#d97706'
      : '#059669';

  return (
    <div className="explanation-card" id="shap-explanation-card">
      {/* Header */}
      <div
        className="explanation-header"
        style={{ background: headerGradient }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="explanation-header-left">
          <div className="explanation-icon" style={{ background: accentColor }}>
            <BrainCircuit size={18} color="white" />
          </div>
          <div>
            <h4 className="explanation-title">AI Explanation</h4>
            <span className="explanation-subtitle">SHAP Feature Attribution</span>
          </div>
        </div>
        <button className="explanation-toggle" id="explanation-toggle">
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {expanded && (
        <div className="explanation-body">
          {/* Natural Language Summary */}
          {naturalExplanation && (
            <div className="explanation-nlp" id="natural-explanation">
              <Info size={16} style={{ color: accentColor, flexShrink: 0, marginTop: 2 }} />
              <p>{naturalExplanation}</p>
            </div>
          )}

          {/* Suppression Notice */}
          {suppressedByRules && (
            <div className="explanation-suppressed" id="suppression-notice">
              <ShieldAlert size={16} />
              <span>{suppressionNote || 'Note: suppressed by safety rules'}</span>
            </div>
          )}

          {/* SHAP Bar Chart */}
          <div className="explanation-chart" id="shap-bar-chart">
            <ResponsiveContainer width="100%" height={chartData.length * 48 + 40}>
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 8, right: 40, left: 10, bottom: 8 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={false}
                  stroke="var(--border)"
                />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: 'var(--text-secondary)' }}
                  axisLine={{ stroke: 'var(--border)' }}
                  tickFormatter={v => v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2)}
                />
                <YAxis
                  type="category"
                  dataKey="label"
                  tick={{ fontSize: 12, fill: 'var(--text-primary)', fontWeight: 500 }}
                  axisLine={false}
                  tickLine={false}
                  width={90}
                />
                <Tooltip content={<SHAPTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                <ReferenceLine x={0} stroke="var(--text-secondary)" strokeWidth={1.5} />
                <Bar
                  dataKey="impact"
                  radius={[0, 4, 4, 0]}
                  barSize={20}
                  animationDuration={600}
                  animationEasing="ease-out"
                >
                  {chartData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Feature Impact Legend */}
          <div className="explanation-legend">
            <div className="explanation-legend-item">
              <span className="legend-dot" style={{ background: '#dc2626' }}></span>
              <span>Increases failure risk</span>
            </div>
            <div className="explanation-legend-item">
              <span className="legend-dot" style={{ background: '#059669' }}></span>
              <span>Reduces failure risk</span>
            </div>
          </div>

          {/* Feature Detail Pills */}
          <div className="explanation-pills" id="feature-impact-pills">
            {explanations.slice(0, 5).map((exp, i) => {
              const isPositive = exp.impact > 0;
              return (
                <div
                  key={i}
                  className={`explanation-pill ${isPositive ? 'pill-danger' : 'pill-success'}`}
                >
                  <span className="pill-indicator">{isPositive ? '🔴' : '🟢'}</span>
                  <span className="pill-feature">
                    {FEATURE_DISPLAY[exp.feature] || exp.feature}
                  </span>
                  <span className="pill-value">
                    {exp.value} {FEATURE_UNITS[exp.feature] || ''}
                  </span>
                  <span className="pill-impact" style={{ color: isPositive ? '#dc2626' : '#059669' }}>
                    {isPositive ? '+' : ''}{exp.impact.toFixed(3)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionExplanationCard;
