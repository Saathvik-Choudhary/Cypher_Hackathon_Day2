import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout for itinerary creation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error_message || 'Server error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

// API functions
export const createItinerary = async (formData) => {
  try {
    const response = await api.post('/api/create-itinerary', formData);
    return response.data;
  } catch (error) {
    console.error('Error creating itinerary:', error);
    throw error;
  }
};

export const getPopularDestinations = async () => {
  try {
    const response = await api.get('/api/destinations/popular');
    return response.data;
  } catch (error) {
    console.error('Error fetching destinations:', error);
    throw error;
  }
};

export const getTravelPreferences = async () => {
  try {
    const response = await api.get('/api/preferences');
    return response.data;
  } catch (error) {
    console.error('Error fetching preferences:', error);
    throw error;
  }
};

export const getBudgetCategories = async () => {
  try {
    const response = await api.get('/api/budget-categories');
    return response.data;
  } catch (error) {
    console.error('Error fetching budget categories:', error);
    throw error;
  }
};

export const getCachedItinerary = async (cacheKey) => {
  try {
    const response = await api.get(`/api/itinerary/${cacheKey}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching cached itinerary:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export default api;
