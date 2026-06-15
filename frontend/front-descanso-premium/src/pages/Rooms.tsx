import { useState, useEffect } from 'react';
import { getRooms, createRoom, updateRoom, changeRoomState, deactivateRoom } from '../api/rooms';
import type { Room, RoomListResponse } from '../api/rooms';
import { Modal } from '../components/Modal';
import { Plus, Pencil, BedDouble, Wrench, CheckCircle2, XCircle } from 'lucide-react';
import { toast } from 'react-toastify';

const ROOM_TYPE_OPTIONS = ['Simple', 'Doble', 'Suite', 'Presidencial'] as const;
const STATE_OPTIONS = ['Disponible', 'Ocupada', 'Mantenimiento'] as const;

const clp = (n: number) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n);


const stateBadge = (state: Room['state']) => {
  const styles: Record<Room['state'], string> = {
    Disponible: 'bg-emerald-100 text-emerald-700',
    Ocupada: 'bg-amber-100 text-amber-700',
    Mantenimiento: 'bg-red-100 text-red-700',
  };
  const icons = {
    Disponible: <CheckCircle2 size={14} className="inline mr-1" />,
    Ocupada: <BedDouble size={14} className="inline mr-1" />,
    Mantenimiento: <Wrench size={14} className="inline mr-1" />,
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[state]}`}>
      {icons[state]}{state}
    </span>
  );
};

const initialForm = {
  number: '',
  room_type: 'Simple' as Room['room_type'],
  capacity: 2,
  price_per_night: 0,
  floor: '' as string | number,
  description: '',
};

export const RoomsPage = () => {
  const [data, setData] = useState<RoomListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [isStateModalOpen, setIsStateModalOpen] = useState(false);
  const [stateTarget, setStateTarget] = useState<Room | null>(null);
  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const fetchRooms = async () => {
    setLoading(true);
    try {
      setData(await getRooms());
    } catch {
      toast.error('Error al cargar las habitaciones');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRooms(); }, []);

  const clearError = (field: string) =>
    setErrors(prev => { const n = { ...prev }; delete n[field]; return n; });

  const validate = () => {
    const e: Record<string, string> = {};
    if (!formData.number.trim()) e.number = 'El número es requerido';
    if (!formData.price_per_night || formData.price_per_night <= 0)
      e.price_per_night = 'El precio debe ser mayor a 0';
    if (!formData.capacity || formData.capacity < 1)
      e.capacity = 'La capacidad debe ser al menos 1';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleOpenModal = (room?: Room) => {
    setErrors({});
    if (room) {
      setEditingRoom(room);
      setFormData({
        number: room.number,
        room_type: room.room_type,
        capacity: room.capacity,
        price_per_night: room.price_per_night,
        floor: room.floor ?? '',
        description: room.description ?? '',
      });
    } else {
      setEditingRoom(null);
      setFormData(initialForm);
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = {
      ...formData,
      floor: formData.floor !== '' ? Number(formData.floor) : null,
    };

    try {
      if (editingRoom) {
        await updateRoom(editingRoom.id, payload);
        toast.success('Habitación actualizada exitosamente');
      } else {
        await createRoom(payload);
        toast.success('Habitación creada exitosamente');
      }
      setIsModalOpen(false);
      fetchRooms();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al guardar la habitación');
    }
  };

  const handleStateChange = async (newState: Room['state']) => {
    if (!stateTarget) return;
    try {
      await changeRoomState(stateTarget.id, newState);
      toast.success(`Estado cambiado a "${newState}"`);
      setIsStateModalOpen(false);
      setStateTarget(null);
      fetchRooms();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al cambiar el estado');
    }
  };

  const handleDeactivate = async (room: Room) => {
    if (!confirm(`¿Desactivar la habitación ${room.number}?`)) return;
    try {
      await deactivateRoom(room.id);
      toast.success('Habitación desactivada');
      fetchRooms();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al desactivar');
    }
  };

  const inputClass = (field: string) =>
    `w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${
      errors[field] ? 'border-red-500' : 'border-stone-300'
    }`;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-serif text-stone-900">Habitaciones</h1>
          <p className="text-sm text-stone-500 mt-1">Gestión de inventario y estados</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-900 transition-colors"
        >
          <Plus size={20} /> Nueva Habitación
        </button>
      </div>

      {/* Summary cards */}
      {data && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          {STATE_OPTIONS.map(state => {
            const count = data.items.filter(r => r.state === state && r.is_active).length;
            const colors: Record<string, string> = {
              Disponible: 'border-emerald-200 bg-emerald-50',
              Ocupada: 'border-amber-200 bg-amber-50',
              Mantenimiento: 'border-red-200 bg-red-50',
            };
            return (
              <div key={state} className={`rounded-xl border p-4 ${colors[state]}`}>
                <p className="text-sm font-medium text-stone-600">{state}</p>
                <p className="text-3xl font-bold text-stone-800 mt-1">{count}</p>
              </div>
            );
          })}
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-stone-500">Cargando habitaciones...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-stone-100 border-b border-stone-200 text-stone-600 text-sm">
                  <th className="px-6 py-4 font-medium">N°</th>
                  <th className="px-6 py-4 font-medium">Tipo</th>
                  <th className="px-6 py-4 font-medium">Capacidad</th>
                  <th className="px-6 py-4 font-medium">Precio/noche</th>
                  <th className="px-6 py-4 font-medium">Estado</th>
                  <th className="px-6 py-4 font-medium text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map(room => (
                  <tr
                    key={room.id}
                    className={`border-b border-stone-100 hover:bg-stone-50 transition-colors ${!room.is_active ? 'opacity-40' : ''}`}
                  >
                    <td className="px-6 py-4 font-bold text-stone-800">{room.number}</td>
                    <td className="px-6 py-4 text-stone-600">{room.room_type}</td>
                    <td className="px-6 py-4 text-stone-600">{room.capacity} pers.</td>
                    <td className="px-6 py-4 text-stone-800 font-medium">
                      {clp(room.price_per_night)}
                    </td>
                    <td className="px-6 py-4">{stateBadge(room.state)}</td>
                    <td className="px-6 py-4 text-right flex justify-end gap-1">
                      {room.is_active && (
                        <>
                          <button
                            title="Cambiar estado"
                            onClick={() => { setStateTarget(room); setIsStateModalOpen(true); }}
                            className="text-stone-400 hover:text-amber-600 p-1 transition-colors"
                          >
                            <BedDouble size={18} />
                          </button>
                          <button
                            title="Editar"
                            onClick={() => handleOpenModal(room)}
                            className="text-stone-400 hover:text-stone-800 p-1 transition-colors"
                          >
                            <Pencil size={18} />
                          </button>
                          <button
                            title="Desactivar"
                            onClick={() => handleDeactivate(room)}
                            className="text-red-300 hover:text-red-600 p-1 transition-colors"
                          >
                            <XCircle size={18} />
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-stone-500">
                      No hay habitaciones registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Crear / Editar */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingRoom ? `Editar Habitación ${editingRoom.number}` : 'Nueva Habitación'}
      >
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Número</label>
              <input
                type="text"
                value={formData.number}
                disabled={!!editingRoom}
                onChange={e => { setFormData({ ...formData, number: e.target.value }); clearError('number'); }}
                className={inputClass('number') + (editingRoom ? ' bg-stone-100 cursor-not-allowed' : '')}
                placeholder="101"
              />
              {errors.number && <p className="text-red-500 text-xs mt-1">{errors.number}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Tipo</label>
              <select
                value={formData.room_type}
                onChange={e => setFormData({ ...formData, room_type: e.target.value as Room['room_type'] })}
                className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
              >
                {ROOM_TYPE_OPTIONS.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Capacidad (personas)</label>
              <input
                type="number"
                min={1} max={20}
                value={formData.capacity}
                onChange={e => { setFormData({ ...formData, capacity: +e.target.value }); clearError('capacity'); }}
                className={inputClass('capacity')}
              />
              {errors.capacity && <p className="text-red-500 text-xs mt-1">{errors.capacity}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Precio por Noche (CLP)</label>
              <input
                type="number"
                min={0}
                step="0.01"
                value={formData.price_per_night}
                onChange={e => { setFormData({ ...formData, price_per_night: +e.target.value }); clearError('price_per_night'); }}
                className={inputClass('price_per_night')}
              />
              {errors.price_per_night && <p className="text-red-500 text-xs mt-1">{errors.price_per_night}</p>}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Piso (opcional)</label>
            <input
              type="number"
              min={0}
              value={formData.floor}
              onChange={e => setFormData({ ...formData, floor: e.target.value })}
              className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
              placeholder="1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Descripción (opcional)</label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200 h-20 resize-none"
              placeholder="Vista al mar, jacuzzi, etc."
            />
          </div>
          <div className="pt-4 flex justify-end gap-3 border-t border-stone-200 mt-6">
            <button type="button" onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-md transition-colors">
              Cancelar
            </button>
            <button type="submit"
              className="px-4 py-2 bg-stone-800 text-white rounded-md hover:bg-stone-900 transition-colors">
              {editingRoom ? 'Actualizar' : 'Crear Habitación'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal: Cambiar Estado */}
      <Modal
        isOpen={isStateModalOpen}
        onClose={() => { setIsStateModalOpen(false); setStateTarget(null); }}
        title={`Cambiar estado — Habitación ${stateTarget?.number}`}
      >
        <p className="text-stone-600 mb-4">Estado actual: {stateTarget && stateBadge(stateTarget.state)}</p>
        <div className="flex flex-col gap-3">
          {STATE_OPTIONS.map(state => (
            <button
              key={state}
              disabled={state === stateTarget?.state}
              onClick={() => handleStateChange(state)}
              className={`w-full py-3 rounded-lg border text-left px-4 font-medium transition-colors ${
                state === stateTarget?.state
                  ? 'bg-stone-100 text-stone-400 cursor-not-allowed border-stone-200'
                  : 'hover:bg-stone-100 border-stone-300 text-stone-700'
              }`}
            >
              {stateBadge(state as Room['state'])} <span className="ml-2">{state}</span>
            </button>
          ))}
        </div>
        <div className="pt-4 flex justify-end border-t border-stone-200 mt-4">
          <button onClick={() => { setIsStateModalOpen(false); setStateTarget(null); }}
            className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-md transition-colors">
            Cancelar
          </button>
        </div>
      </Modal>
    </div>
  );
};
