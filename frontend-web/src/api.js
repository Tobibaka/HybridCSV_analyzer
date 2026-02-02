import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth endpoints
export const authAPI = {
  login: (username, password) => 
    api.post('/auth/login/', { username, password }),
  
  register: (username, email, password) => 
    api.post('/auth/register/', { username, email, password }),
  
  logout: () => 
    api.post('/auth/logout/'),
  
  getCurrentUser: () => 
    api.get('/auth/user/'),
};

// Dataset endpoints
export const datasetAPI = {
  getAll: () => 
    api.get('/datasets/'),
  
  getById: (id) => 
    api.get(`/datasets/${id}/`),
  
  getSummary: (id) => 
    api.get(`/datasets/${id}/summary/`),
  
  getRecords: (id) => 
    api.get(`/datasets/${id}/records/`),
  
  delete: (id) => 
    api.delete(`/datasets/${id}/`),
  
  uploadCSV: (file, name) => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    
    return api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  downloadReport: (id) => 
    `${API_BASE_URL}/datasets/${id}/report/`,
};

// Health check
export const healthCheck = () => api.get('/health/');

export default api;
