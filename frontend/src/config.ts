const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const apiUrl = rawApiUrl.startsWith('http') ? rawApiUrl : `https://${rawApiUrl}`;
export const API_BASE_URL = apiUrl.endsWith('/api') ? apiUrl : `${apiUrl}/api`;