import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
};

export const projectsAPI = {
  list: () => api.get('/api/projects'),
  create: (data) => api.post('/api/projects', data),
  get: (id) => api.get(`/api/projects/${id}`),
  update: (id, data) => api.put(`/api/projects/${id}`, data),
  delete: (id) => api.delete(`/api/projects/${id}`),
};

export const generateAPI = {
  outline: (data) => api.post('/api/generate/outline', data),
  content: (data) => api.post('/api/generate/content', data),
  addSection: (projectId, title, order) => 
    api.post(`/api/generate/add-section/${projectId}`, null, {
      params: { section_title: title, order }
    }),
};

export const refineAPI = {
  refine: (data) => api.post('/api/refine/refine', data),
  feedback: (data) => api.post('/api/refine/feedback', data),
  revert: (data) => api.post('/api/refine/revert', data),
};

export const exportAPI = {
  docx: (projectId) => 
    api.post('/api/export/docx', { project_id: projectId }, {
      responseType: 'blob'
    }),
  pptx: (projectId) => 
    api.post('/api/export/pptx', { project_id: projectId }, {
      responseType: 'blob'
    }),
};
