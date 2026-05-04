import React, { useState, useContext } from 'react';
import { Activity, Mail, Lock } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import { registerUser } from '../services/authApi';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [isRegistering, setIsRegistering] = useState(false);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('engineer');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (isRegistering) {
      try {
        await registerUser({ name, email, password, role });
        // After register, automatically login
        const res = await login(email, password);
        if (!res.success) setError(res.error);
        else navigate('/');
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to register');
      }
    } else {
      const res = await login(email, password);
      if (!res.success) setError(res.error);
      else navigate('/');
    }
    setLoading(false);
  };

  return (
    <div className="layout-container" style={{ alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-main)' }}>
      <div className="card" style={{ width: '400px', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'center', color: 'var(--primary)', marginBottom: '1rem' }}>
            <Activity size={48} />
          </div>
          <h1 className="page-title">{isRegistering ? 'Create Account' : 'Welcome Back'}</h1>
          <p className="page-subtitle">Automotive Predictive Maintenance System</p>
        </div>

        {error && (
          <div className="badge badge-danger" style={{ width: '100%', padding: '0.75rem', marginBottom: '1.5rem', justifyContent: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {isRegistering && (
            <div>
              <label className="text-sm font-medium mb-1 block">Full Name</label>
              <div className="header-search" style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white' }}>
                <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="John Doe" required />
              </div>
            </div>
          )}

          <div>
            <label className="text-sm font-medium mb-1 block">Email</label>
            <div className="header-search" style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white' }}>
              <Mail size={16} className="text-muted" />
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="user@example.com" required />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Password</label>
            <div className="header-search" style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white' }}>
              <Lock size={16} className="text-muted" />
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
            </div>
          </div>

          {isRegistering && (
            <div>
              <label className="text-sm font-medium mb-1 block">Role</label>
              <select 
                value={role} 
                onChange={e => setRole(e.target.value)} 
                className="header-search" 
                style={{ margin: 0, width: '100%', border: '1px solid var(--border)', backgroundColor: 'white', outline: 'none' }}
              >
                <option value="admin">Admin</option>
                <option value="engineer">Engineer</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
          )}

          <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem', padding: '0.75rem' }} disabled={loading}>
            {loading ? 'Processing...' : isRegistering ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <button className="btn btn-secondary" style={{ border: 'none', backgroundColor: 'transparent' }} onClick={() => setIsRegistering(!isRegistering)}>
            {isRegistering ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
