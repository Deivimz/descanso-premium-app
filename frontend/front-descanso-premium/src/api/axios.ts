import axios from 'axios';

export const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Crucial para enviar y recibir cookies HttpOnly
});

// Interceptor para manejar errores 401 (No autorizado) a nivel global
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Podríamos limpiar el store de Zustand aquí si es necesario
      console.warn("Unauthorized access - 401");
    }
    return Promise.reject(error);
  }
);
