import { api } from './axios';

export interface RoomTypeStats {
  total: number;
  disponible: number;
  ocupada: number;
  mantenimiento: number;
}

export interface DashboardStats {
  guests: {
    total_active: number;
    currently_in_hotel: number;
  };
  rooms: {
    total: number;
    disponible: number;
    ocupada: number;
    mantenimiento: number;
    by_type: Record<string, RoomTypeStats>;
  };
  reservations: {
    total: number;
    confirmada: number;
    cancelada: number;
    completada: number;
  };
  revenue: {
    confirmed_total_clp: number;
    historical_total_clp: number;
  };
}

export const getDashboardStats = (): Promise<DashboardStats> =>
  api.get('/dashboard/stats').then(r => r.data);
