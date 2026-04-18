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
  API.post('/auth/register', { username, email, password, role });

export const login = (email, password) =>
  API.post('/auth/login', { email, password });

// Conferences
export const getConferences = () => API.get('/conferences');
export const createConference = (data) => API.post('/conferences', data);
export const getConference = (id) => API.get(`/conferences/${id}`);

// Papers
export const getPapers = (params) => API.get('/papers', { params });
export const submitPaper = (data) => API.post('/papers', data);
export const getPaper = (id) => API.get(`/papers/${id}`);
export const updatePaper = (id, data) => API.put(`/papers/${id}`, data);
export const deletePaper = (id) => API.delete(`/papers/${id}`);
export const updatePaperStatus = (id, status) =>
  API.put(`/papers/${id}/status`, { status });

// Reviews
export const getReviews = (paperId) => API.get(`/papers/${paperId}/reviews`);
export const submitReview = (paperId, data) =>
  API.post(`/papers/${paperId}/reviews`, data);

// Dashboard
export const getDashboard = () => API.get('/dashboard');

// Subscriptions
export const subscribe = (email) => API.post('/subscribe', { email });
export const getSubscriberCount = () => API.get('/subscribers');

export default API;
