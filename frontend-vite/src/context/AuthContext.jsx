import React, { createContext, useState, useEffect } from 'react';
import { loginUser } from '../services/authApi';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  // When app loads, try to decode token to get user info if needed
  useEffect(() => {
    if (token) {
      // In a real app we might fetch user profile here. For now, decode simple details from token or use generic placeholder
      const savedRole = localStorage.getItem('role') || 'engineer';
      setUser({ name: "User", role: savedRole });
    } else {
      setUser(null);
    }
    setLoading(false);
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
