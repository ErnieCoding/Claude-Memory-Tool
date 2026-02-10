import axios from 'axios';

// В production используем относительный путь через nginx proxy
// В dev режиме можно указать VITE_API_URL в .env
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  async uploadFiles(files, onProgress) {
    const formData = new FormData();

    for (let file of files) {
      formData.append('files[]', file);
    }

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
    return response.data;
  },

  async listFiles() {
    const response = await api.get('/files');
    return response.data;
  },

  async deleteFile(filepath) {
    const response = await api.delete(`/files/${filepath}`);
    return response.data;
  },

  async clearAllFiles() {
    const response = await api.post('/files/clear');
    return response.data;
  },

  async sendQuery(query, maxTokens = 8000) {
    const response = await api.post('/query', {
      query,
      max_tokens: maxTokens
    });
    return response.data;
  },

  createQueryStream(query, maxTokens = 8000) {
    return fetch(`${API_BASE_URL}/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_tokens: maxTokens
      })
    });
  },

  async listResponses() {
    const response = await api.get('/responses');
    return response.data;
  },

  async getResponse(filepath) {
    const response = await api.get(`/responses/${filepath}`);
    return response.data;
  },

  async deleteResponse(filepath) {
    const response = await api.delete(`/responses/${filepath}`);
    return response.data;
  }
};
