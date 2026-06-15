import { api } from './axios';
import type { User } from '../store/authStore';

export const getUsers = async (skip = 0, limit = 100) => {
  const { data } = await api.get<User[]>('/users', {
    params: { skip, limit }
  });
  return data;
};

export const createUser = async (user: Partial<User> & { password?: string }) => {
  const { data } = await api.post<User>('/users', user);
  return data;
};

export const updateUser = async (id: string, user: Partial<User> & { password?: string }) => {
  const { data } = await api.patch<User>(`/users/${id}`, user);
  return data;
};

export const deleteUser = async (id: string) => {
  const { data } = await api.delete(`/users/${id}`);
  return data;
};
