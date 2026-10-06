// API client for TerraSafe - uses VITE_API_URL from env
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorData = {};
      try {
        errorData = await response.json();
      } catch {}
      throw new ApiError(
        errorData.detail || errorData.message || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }
    
    if (response.status === 204) return null;
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    
    // Network error / offline
    throw new ApiError(
      'Network error. Please check your connection.',
      0,
      { originalError: error.message }
    );
  }
}

export const api = {
  get: (endpoint) => request(endpoint, { method: 'GET' }),
  post: (endpoint, data) => request(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  patch: (endpoint, data) => request(endpoint, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (endpoint) => request(endpoint, { method: 'DELETE' }),
};

// API methods
export const riskApi = {
  getConfig: () => api.get('/config/risk-thresholds'),
  searchLocations: (q) => api.get(`/locations/search?q=${encodeURIComponent(q)}`),
  getRisk: (zoneId) => api.get(`/risk/${zoneId}`),
  getRiskHistory: (zoneId, days = 7) => api.get(`/risk/${zoneId}/history?days=${days}`),
  getCounterfactual: (zoneId) => api.get(`/risk/${zoneId}/counterfactual`),
  getMapRiskZones: (location = 'Nilgiris') => api.get(`/map/risk-zones?location=${encodeURIComponent(location)}`),
  simulate: (data) => api.post('/simulate', data),
};

export const safeZonesApi = {
  getNearby: (lat, lon, radiusKm = 10) => 
    api.get(`/safe-zones?latitude=${lat}&longitude=${lon}&radius_km=${radiusKm}`),
};

export const rescueApi = {
  getNearby: (lat, lon) => api.get(`/rescue/nearby?latitude=${lat}&longitude=${lon}`),
  getRoute: (origin, destination) => 
    api.get(`/rescue/route?latitude=${origin.lat}&longitude=${origin.lon}&destination_lat=${destination.lat}&destination_lon=${destination.lon}`),
};

export const alertsApi = {
  getPreferences: () => api.get('/alerts/preferences'),
  list: (limit = 100) => api.get(`/alerts?limit=${limit}`),
  get: (id) => api.get(`/alerts/${id}`),
  create: (data) => api.post('/alerts', data),
  update: (id, data) => api.patch(`/alerts/${id}`, data),
  delete: (id) => api.delete(`/alerts/${id}`),
  transition: (id, event) => api.post(`/alerts/${id}/transition`, { event }),
  getAudit: (id) => api.get(`/alerts/${id}/audit`),
};

export const dataSourcesApi = {
  getHealth: () => api.get('/data-sources'),
};

export const copilotApi = {
  query: (question, zoneId) => {
    const params = new URLSearchParams({ question });
    if (zoneId) params.append('zone_id', zoneId);
    return api.post('/copilot', null, { params });
  },
};

export const healthApi = {
  check: () => api.get('/health'),
  checkV1: () => api.get('/api/v1/health'),
};

export { ApiError };