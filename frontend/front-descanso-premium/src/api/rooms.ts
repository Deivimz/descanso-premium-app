import { api } from './axios';

export interface Room {
  id: string;
  number: string;
  room_type: 'Simple' | 'Doble' | 'Suite' | 'Presidencial';
  capacity: number;
  state: 'Disponible' | 'Ocupada' | 'Mantenimiento';
  price_per_night: number;
  floor: number | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoomListResponse {
  items: Room[];
  total: number;
  skip: number;
  limit: number;
}

export const getRooms = (skip = 0, limit = 100, onlyAvailable = false): Promise<RoomListResponse> =>
  api.get('/rooms', { params: { skip, limit, only_available: onlyAvailable } }).then(r => r.data);

export const getRoom = (id: string): Promise<Room> =>
  api.get(`/rooms/${id}`).then(r => r.data);

export const createRoom = (data: Partial<Room>): Promise<Room> =>
  api.post('/rooms', data).then(r => r.data);

export const updateRoom = (id: string, data: Partial<Room>): Promise<Room> =>
  api.patch(`/rooms/${id}`, data).then(r => r.data);

export const changeRoomState = (id: string, state: Room['state']): Promise<Room> =>
  api.patch(`/rooms/${id}/state`, { state }).then(r => r.data);

export const deactivateRoom = (id: string): Promise<Room> =>
  api.delete(`/rooms/${id}`).then(r => r.data);
