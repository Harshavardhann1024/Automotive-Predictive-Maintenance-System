import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings, AlertTriangle, Activity, PenToolIcon, TrendingDown } from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { vehiclesData, componentHealthData, vehicleSensorData, predictiveInsights } from '../data/mockData';

const VehicleDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Use mock data or fallback to the first one
  const vehicle = vehiclesData.find(v => v.id === id) || vehiclesData[0];

  return (
    <div>
      <div className="page-header" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/vehicles')} style={{ padding: '0.5rem' }}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="page-title">{vehicle.model}</h1>
            <p className="page-subtitle">{vehicle.regNumber} • {vehicle.id} • {vehicle.mileage.toLocaleString()} km</p>
          </div>
        </div>
      </div>

      <div className="grid-cols-12 mb-4">
        {/* Left Col - Overview */}
        <div className="col-span-4" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card">
            <h3 className="card-title mb-4">Vehicle Health Status</h3>
            <div style={{ display: 'flex', justifyContent: 'center', margin: '2rem 0' }}>
              <div style={{ position: 'relative', width: '150px', height: '150px', borderRadius: '50%', border: `12px solid ${vehicle.healthScore > 80 ? 'var(--success)' : vehicle.healthScore > 50 ? 'var(--warning)' : 'var(--danger)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                <span style={{ fontSize: '2.5rem', fontWeight: 700 }}>{vehicle.healthScore}</span>
                <span className="text-muted text-xs">/ 100</span>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="flex justify-between mb-2 text-sm font-medium"><span>Risk Tier</span> <span className="text-danger">{vehicle.riskTier}</span></div>
              <div className="flex justify-between mb-2 text-sm font-medium"><span>Status</span> <span className="text-success">{vehicle.status}</span></div>
              <div className="flex justify-between text-sm font-medium"><span>Last Service</span> <span className="text-muted">14 days ago</span></div>
            </div>
          </div>

          <div className="card">
            <h3 className="card-title mb-4">Component Health</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {componentHealthData.map(c => (
                <div key={c.name}>
                  <div className="flex justify-between text-sm font-medium mb-1">
                    <span>{c.name}</span>
                    <span style={{ color: c.health > 80 ? 'var(--success)' : c.health > 50 ? 'var(--warning)' : 'var(--danger)' }}>{c.health}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: 'var(--bg-main)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ 
                      width: `${c.health}%`, 
                      height: '100%', 
                      background: c.health > 80 ? 'var(--success)' : c.health > 50 ? 'var(--warning)' : 'var(--danger)' 
                    }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col - Charts & Insights */}
        <div className="col-span-8" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Sensor Analytics (Engine Temp & Vibration)</h3>
              <span className="badge badge-primary"><Activity size={14}/> Live Data</span>
            </div>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={vehicleSensorData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis yAxisId="left" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} domain={[70, 120]} />
                  <YAxis yAxisId="right" orientation="right" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} domain={[1, 5]} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid var(--border)' }} />
                  <Line yAxisId="left" type="monotone" dataKey="temp" name="Temperature (°C)" stroke="var(--primary)" strokeWidth={3} dot={false} />
                  <Line yAxisId="right" type="monotone" dataKey="vibration" name="Vibration (g)" stroke="var(--warning)" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 className="card-title mb-4">AI Predictive Insights</h3>
            {predictiveInsights.map(insight => (
              <div key={insight.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', padding: '1rem', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                <div style={{ padding: '0.75rem', backgroundColor: 'var(--danger-light)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
                  <AlertTriangle size={24} />
                </div>
                <div style={{ flex: 1 }}>
                  <div className="flex justify-between items-center mb-1">
                    <h4 className="font-medium">{insight.component} Failure Predicted</h4>
                    <span className="badge badge-danger">{insight.probability}% Probability</span>
                  </div>
                  <p className="text-sm text-muted mb-2">Estimated time to failure: <strong className="text-primary">{insight.timeToFailure}</strong></p>
                  <p className="text-sm">Cost avoidance: <strong className="text-success">{insight.costImpact}</strong> if serviced immediately.</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VehicleDetailPage;
