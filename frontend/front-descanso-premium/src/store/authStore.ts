import { create } from 'zustand';
import { api } from '../api/axios';

export interface User {
  id: string;
  username: string;
  email: string;
  rut: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'staff';
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isCheckingAuth: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  isCheckingAuth: true,
  isAuthenticated: false,

  login: async (username, password) => {
    set({ isLoading: true });
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      // Tras el login exitoso, obtenemos la información del usuario
      const { data: user } = await api.get<User>('/auth/me');
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await api.post('/auth/logout');
      set({ user: null, isAuthenticated: false, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      console.error('Logout error', error);
    }
  },

  checkAuth: async () => {
    set({ isCheckingAuth: true });
    try {
      const { data: user } = await api.get<User>('/auth/me');
      set({ user, isAuthenticated: true, isCheckingAuth: false });
    } catch (error) {
      // 401 o cualquier error significa que no hay sesión activa
      set({ user: null, isAuthenticated: false, isCheckingAuth: false });
    }
  }
}));
