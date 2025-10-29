import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Vehicle search
export const searchVehicles = async (params: {
  lat: number;
  lng: number;
  radius?: number;
  type?: string;
  time_range?: string;
}) => {
  const response = await api.get('/search-vehicles', { params });
  return response.data.vehicles;
};

// Storage analysis
export const getStorageAnalysis = async (params: {
  lat: number;
  lng: number;
  radius?: number;
}) => {
  const response = await api.get('/storage-analysis', { params });
  return response.data;
};

// Aircraft search
export const searchAircraft = async (params: {
  lat: number;
  lng: number;
  radius?: number;
}) => {
  const response = await api.get('/aircraft-search', { params });
  return response.data.aircraft;
};

// Image upload for detection
export const uploadImageForDetection = async (data: {
  image: string;
  coordinates: {
    lat: number;
    lng: number;
    zoom: number;
  };
}) => {
  const response = await api.post('/upload-image', data);
  return response.data;
};

// Long-term stopped vehicle detection
export const detectLongTermStopped = async (params: {
  lat: number;
  lng: number;
  radius?: number;
  days_back?: number;
}) => {
  const response = await api.get('/long-term-stopped', { params });
  return response.data;
};

// Vehicle history
export const getVehicleHistory = async (vehicleId: number) => {
  const response = await api.get(`/vehicle-history/${vehicleId}`);
  return response.data;
};

// Area summary
export const getAreaSummary = async (params: {
  lat: number;
  lng: number;
  radius?: number;
  days_back?: number;
}) => {
  const response = await api.get('/area-summary', { params });
  return response.data;
};

// South Korea satellite data
export const getSouthKoreaCoverage = async (params: {
  lat: number;
  lng: number;
  radius?: number;
}) => {
  const response = await api.get('/south-korea/coverage', { params });
  return response.data;
};

export const getRecentImagery = async (params: {
  lat: number;
  lng: number;
  days_back?: number;
}) => {
  const response = await api.get('/south-korea/imagery', { params });
  return response.data;
};

export const getCitiesCoverage = async () => {
  const response = await api.get('/south-korea/cities');
  return response.data;
};

export const getDownloadGuide = async () => {
  const response = await api.get('/south-korea/download-guide');
  return response.data;
};

// Vehicle details
export const getVehicleDetails = async (vehicleId: number) => {
  const response = await api.get(`/vehicle/${vehicleId}/details`);
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

