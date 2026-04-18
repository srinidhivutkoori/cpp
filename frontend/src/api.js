import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const API = axios.create({
  baseURL: API_BASE,
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('paperhub_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

API.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('paperhub_user');
      localStorage.removeItem('paperhub_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const register = (username, email, password, role) =>
  API.post('/api/auth/register', { username, email, password, role });

export const login = (email, password) =>
  API.post('/api/auth/login', { email, password });

// Conferences
export const getConferences = () => API.get('/api/conferences');
export const createConference = (data) => API.post('/api/conferences', data);
export const getConference = (id) => API.get(`/api/conferences/${id}`);

// Papers
export const getPapers = (params) => API.get('/api/papers', { params });
export const submitPaper = (data) => API.post('/api/papers', data);
export const getPaper = (id) => API.get(`/api/papers/${id}`);
export const updatePaper = (id, data) => API.put(`/api/papers/${id}`, data);
export const deletePaper = (id) => API.delete(`/api/papers/${id}`);
export const updatePaperStatus = (id, status) =>
  API.put(`/api/papers/${id}/status`, { status });

// Reviews
export const getReviews = (paperId) => API.get(`/api/papers/${paperId}/reviews`);
export const submitReview = (paperId, data) =>
  API.post(`/api/papers/${paperId}/reviews`, data);

// Dashboard
export const getDashboard = () => API.get('/api/dashboard');

// Subscriptions
export const subscribe = (email) => API.post('/api/subscribe', { email });
export const getSubscriberCount = () => API.get('/api/subscribers');

export default API;
