import React, { createContext, useState, useEffect } from 'react';
import { loginUser } from '../services/authApi';

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [user, setUser] = useState(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      const savedRole = localStorage.getItem('role') || 'engineer';
      return { name: "User", role: savedRole };
    }
    return null;
  });
  const loading = false;

  useEffect(() => {
    if (!token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setUser(null);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const data = await loginUser(email, password);
      // data should contain access_token
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        // decode or fetch user to set user state
        const inferredRole = data.user?.role || (email.includes('admin') ? 'admin' : email.includes('viewer') ? 'viewer' : 'engineer');
        localStorage.setItem('role', inferredRole);
        setUser({ name: email.split('@')[0], email, role: inferredRole }); 
        return { success: true };
      }
      return { success: false, error: 'No token received' };
    } catch (err) {
      console.error(err);
      return { success: false, error: err.response?.data?.detail || 'Login failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
