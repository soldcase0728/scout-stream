import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (email: string, name: string, password: string) =>
  api.post('/auth/register', { email, name, password });

export const login = (email: string, password: string) =>
  api.post('/auth/login', { email, password });

export const getMe = () => api.get('/auth/me');

// Athletes
export const listAthletes = () => api.get('/athletes');
export const createAthlete = (data: {
  first_name: string;
  last_name: string;
  handedness: string;
  primary_swing_type: string;
}) => api.post('/athletes', data);
export const getAthlete = (id: string) => api.get(`/athletes/${id}`);
export const updateAthlete = (id: string, data: Record<string, unknown>) =>
  api.patch(`/athletes/${id}`, data);
export const listAthleteSessions = (athleteId: string) =>
  api.get(`/athletes/${athleteId}/sessions`);
export const getAthleteTrends = (athleteId: string) =>
  api.get(`/athletes/${athleteId}/trends`);

// Sessions
export const createSession = (data: {
  athlete_id: string;
  session_type?: string;
  notes?: string;
}) => api.post('/sessions', data);
export const getSession = (id: string) => api.get(`/sessions/${id}`);
export const listSessionSwings = (sessionId: string) =>
  api.get(`/sessions/${sessionId}/swings`);
export const uploadSwing = (sessionId: string, file: File, swingType: string) => {
  const form = new FormData();
  form.append('file', file);
  form.append('swing_type', swingType);
  return api.post(`/sessions/${sessionId}/swings/upload`, form);
};

// Swings
export const getSwing = (id: string) => api.get(`/swings/${id}`);
export const getSwingStatus = (id: string) => api.get(`/swings/${id}/status`);
export const getSwingLandmarks = (id: string) => api.get(`/swings/${id}/landmarks`);
export const getSwingDrills = (id: string) => api.get(`/swings/${id}/drills`);
export const editEvents = (id: string, data: {
  final_start_frame: number;
  final_launch_frame: number;
  final_contact_frame: number;
}) => api.patch(`/swings/${id}/events`, data);
export const updateSwingNotes = (id: string, notes: string) =>
  api.patch(`/swings/${id}/notes`, { notes });
export const compareSwings = (id: string, otherId: string) =>
  api.get(`/swings/${id}/comparison/${otherId}`);

export default api;
