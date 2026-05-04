import React, { useState, useEffect } from 'react';
import { User, Mail, Shield, Loader2, AlertCircle } from 'lucide-react';
import { apiClient } from '../services/authApi';

const ProfilePage = () => {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const res = await apiClient.get('/users/me');
        setProfile(res.data);
      } catch (err) {
        setError('Failed to load profile. Please make sure backend is running.');
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '4rem', display: 'flex', justifyContent: 'center' }}>
        <Loader2 className="animate-spin text-primary" size={32} />
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Profile</h1>
          <p className="page-subtitle">Your account and credentials</p>
        </div>
      </div>

      {error ? (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger-light)', color: 'var(--danger)', borderRadius: 'var(--radius-md)', display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1.5rem' }}>
          <AlertCircle size={20} />
          {error}
        </div>
      ) : (
        <div className="grid-cols-12">
          <div className="col-span-12 md:col-span-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card text-center" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
               <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', fontWeight: 600, marginBottom: '1rem' }}>
                 {profile?.name?.charAt(0).toUpperCase() || <User size={32} />}
               </div>
               <h3 className="card-title" style={{ marginBottom: '0.25rem' }}>{profile?.name || 'Administrator'}</h3>
               <p className="text-muted text-sm" style={{ marginBottom: '1rem' }}>{profile?.email || 'admin@autopredict.io'}</p>
               <span className="badge badge-primary">{profile?.role || 'Admin'}</span>
            </div>
            
            <div className="card">
               <h3 className="card-title mb-4">Account Details</h3>
               <div className="flex justify-between py-2 border-b">
                 <span className="text-muted text-sm"><Mail size={16} className="inline mr-2" /> Email</span>
                 <span className="text-sm font-medium">{profile?.email || 'admin@autopredict.io'}</span>
               </div>
               <div className="flex justify-between py-2 border-b">
                 <span className="text-muted text-sm"><Shield size={16} className="inline mr-2" /> Role</span>
                 <span className="text-sm font-medium" style={{ textTransform: 'capitalize' }}>{profile?.role || 'Admin'}</span>
               </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
