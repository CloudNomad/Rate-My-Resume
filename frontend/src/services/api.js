import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const saveVersion = async (file, userId, versionName) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);
  formData.append('version_name', versionName);
  return api.post('/save-version', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getVersions = async (userId) => {
  return api.get(`/versions/${userId}`);
};

export const compareVersions = async (version1Id, version2Id) => {
  return api.get(`/compare/${version1Id}/${version2Id}`);
};

export const deleteVersion = async (versionId) => {
  return api.delete(`/versions/${versionId}`);
};

export const generateTestData = async (count) => {
  return api.post('/generate-test-data', { count });
};

export const clearTestData = async () => {
  return api.post('/clear-test-data');
}; 