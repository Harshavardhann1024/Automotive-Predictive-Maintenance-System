import React, { useState, useEffect } from 'react';
import { Search, Filter, Plus, ChevronRight, Loader2, X } from 'lucide-react';
import { fetchVehicles, createVehicle } from '../services/api';
import { useNavigate } from 'react-router-dom';

const VehiclesPage = () => {
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const [showModal, setShowModal] = useState(false);
  const [newVehicle, setNewVehicle] = useState({ registration_number: '', name: '', mileage: '' });
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    async function loadVehicles() {
      try {
        const data = await fetchVehicles();
        setVehicles(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadVehicles();
  }, []);

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    setAdding(true);
    try {
      const added = await createVehicle({
        registration_number: newVehicle.registration_number,
        name: newVehicle.name,
        mileage: parseInt(newVehicle.mileage) || 0,
        health_score: 100
      });
      setVehicles([added, ...vehicles]);
      setShowModal(false);
      setNewVehicle({ registration_number: '', name: '', mileage: '' });
      alert("Vehicle added successfully!");
    } catch (err) {
      alert("Failed to add vehicle.");
      console.error(err);
    } finally {
      setAdding(false);
    }
  };

  const filteredVehicles = vehicles.filter(v => {
    if (!searchTerm) return true;
    const s = searchTerm.toLowerCase();
    const idStr = v.id || '';
    const regStr = v.registration_number || v.regNumber || '';
    const nameStr = v.model || v.name || '';
    return idStr.toLowerCase().includes(s) || regStr.toLowerCase().includes(s) || nameStr.toLowerCase().includes(s);
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Fleet Vehicles</h1>
          <p className="page-subtitle">Manage and monitor your connected vehicles</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} /> Add Vehicle
        </button>
      </div>

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div className="card" style={{ width: '400px', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 className="card-title" style={{ margin: 0 }}>Add New Vehicle</h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}><X size={20} /></button>
            </div>
            
            <form onSubmit={handleAddSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="text-sm font-medium mb-1 block">Registration Number</label>
                <div className="header-search" style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white' }}>
                  <input type="text" value={newVehicle.registration_number} onChange={e => setNewVehicle({...newVehicle, registration_number: e.target.value})} placeholder="e.g. MH12AB3456" required />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Vehicle Name/Model</label>
                <div className="header-search" style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white' }}>
                  <input type="text" value={newVehicle.name} onChange={e => setNewVehicle({...newVehicle, name: e.target.value})} placeholder="e.g. Tata Nexon EV" required />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Current Mileage</label>
                <div className="header-search" style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white' }}>
                  <input type="number" value={newVehicle.mileage} onChange={e => setNewVehicle({...newVehicle, mileage: e.target.value})} placeholder="e.g. 15000" />
                </div>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={adding}>
                  {adding ? 'Adding...' : 'Add Vehicle'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card mb-4" style={{ padding: '1rem 1.5rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div className="header-search" style={{ margin: 0, flex: 1, backgroundColor: 'white', border: '1px solid var(--border)' }}>
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Search by Reg Number, ID, or Model..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ padding: '3rem', display: 'flex', justifyContent: 'center' }}>
            <Loader2 className="animate-spin text-primary" size={32} />
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vehicle ID</th>
                  <th>Registration</th>
                  <th>Model</th>
                  <th>Mileage (km)</th>
                  <th>Health Score</th>
                  <th>Risk Tier</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredVehicles.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="text-center py-4 text-muted">No vehicles found matching search.</td>
                  </tr>
                ) : filteredVehicles.map((v, idx) => (
                  <tr key={v.id || idx} onClick={() => navigate(`/vehicles/${v.id}`)} style={{ cursor: 'pointer' }}>
                    <td className="font-medium text-primary">{v.id ? v.id.slice(0, 8) : 'N/A'}</td>
                    <td className="font-medium">{v.registration_number || v.regNumber}</td>
                    <td>{v.model || v.name}</td>
                    <td>{(v.mileage || 0).toLocaleString()}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '40px', height: '6px', background: 'var(--bg-main)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ 
                            width: `${v.healthScore || v.health_score || 90}%`, 
                            height: '100%', 
                            background: (v.healthScore || v.health_score || 90) > 85 ? 'var(--success)' : (v.healthScore || v.health_score || 90) > 60 ? 'var(--warning)' : 'var(--danger)' 
                          }}></div>
                        </div>
                        <span className="text-xs font-medium">{v.healthScore || v.health_score || 90}/100</span>
                      </div>
                    </td>
                    <td>
                      <span className={`badge badge-${(v.riskTier || v.risk_level || 'Low') === 'Critical' ? 'danger' : (v.riskTier || v.risk_level || 'Low') === 'High' ? 'warning' : (v.riskTier || v.risk_level || 'Low') === 'Medium' ? 'info' : 'success'}`}>
                        {v.riskTier || v.risk_level || 'Low'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${(v.status || 'Active') === 'Active' ? 'success' : (v.status || 'Active') === 'Maintenance' ? 'warning' : 'neutral'}`}>
                        {v.status || 'Active'}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={(e) => { e.stopPropagation(); navigate(`/vehicles/${v.id}`); }}>
                        <ChevronRight size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default VehiclesPage;
