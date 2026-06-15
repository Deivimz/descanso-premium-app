import { api } from './axios';

export interface Reservation {
  id: string;
  guest_id: string;
  room_id: string;
  check_in: string;
  check_out: string;
  status: 'Confirmada' | 'Cancelada' | 'Completada';
  total_price: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReservationListResponse {
  items: Reservation[];
  total: number;
  skip: number;
  limit: number;
}

export interface CreateReservationPayload {
  guest_id: string;
  room_id: string;
  check_in: string;
  check_out: string;
  notes?: string;
}

export const getReservations = (skip = 0, limit = 100): Promise<ReservationListResponse> =>
  api.get('/reservations', { params: { skip, limit } }).then(r => r.data);

export const getGuestReservations = (guestId: string, skip = 0, limit = 100): Promise<ReservationListResponse> =>
  api.get(`/reservations/guest/${guestId}`, { params: { skip, limit } }).then(r => r.data);

export const createReservation = (data: CreateReservationPayload): Promise<Reservation> =>
  api.post('/reservations', data).then(r => r.data);

export const cancelReservation = (id: string): Promise<Reservation> =>
  api.patch(`/reservations/${id}/cancel`).then(r => r.data);

export const completeReservation = (id: string): Promise<Reservation> =>
  api.patch(`/reservations/${id}/complete`).then(r => r.data);
