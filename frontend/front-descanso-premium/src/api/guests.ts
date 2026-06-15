import { api } from './axios';

export interface Guest {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth?: string;
  nationality?: string;
  address?: string;
  document_type: string;
  document_number: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GuestListResponse {
  items: Guest[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const getGuests = async (page = 1, size = 20, search = '', include_inactive = false) => {
  const { data } = await api.get<GuestListResponse>('/guests', {
    params: { page, size, search, include_inactive }
  });
  return data;
};

export const createGuest = async (guest: Partial<Guest>) => {
  const { data } = await api.post<Guest>('/guests', guest);
  return data;
};

export const updateGuest = async (id: string, guest: Partial<Guest>) => {
  const { data } = await api.patch<Guest>(`/guests/${id}`, guest);
  return data;
};

export const deleteGuest = async (id: string) => {
  const { data } = await api.delete(`/guests/${id}`);
  return data;
};
