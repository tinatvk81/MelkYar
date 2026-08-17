
import api from './client';

export const getProperties = () => api.get('/properties/');
export const getPropertyDetail = (id) => api.get(`/properties/${id}/`);
export const createProperty = (data) => api.post('/properties/', data);
export const updateProperty = (id, data) => api.put(`/properties/${id}/`, data);
export const deleteProperty = (id) => api.delete(`/properties/${id}/`);
