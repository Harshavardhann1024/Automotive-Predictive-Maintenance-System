import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE,
});

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function loginUser(email, password) {
  // Use login-json if backend prefers json, or OAuth2 formData
  const response = await apiClient.post(`/auth/login-json`, {
    email,
    password
  });
  return response.data; // { access_token, token_type, user: {...} }
}

export async function registerUser(userData) {
  const response = await apiClient.post(`/auth/register`, userData);
  return response.data;
}
