const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_BASE_URL = apiUrl.endsWith('/api') ? apiUrl : `${apiUrl}/api`;