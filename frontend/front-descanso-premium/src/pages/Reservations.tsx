import { useState, useEffect } from 'react';
import { getReservations, createReservation, cancelReservation, completeReservation } from '../api/reservations';
import type { Reservation, ReservationListResponse } from '../api/reservations';
import { getRooms } from '../api/rooms';
import type { Room } from '../api/rooms';
import { getGuests } from '../api/guests';
import type { Guest } from '../api/guests';
import { Modal } from '../components/Modal';
import { Plus, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { toast } from 'react-toastify';

const clp = (n: number) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n);


const statusBadge = (status: Reservation['status']) => {
  const styles: Record<Reservation['status'], string> = {
    Confirmada: 'bg-emerald-100 text-emerald-700',
    Cancelada: 'bg-red-100 text-red-700',
    Completada: 'bg-stone-100 text-stone-500',
  };
  const icons = {
    Confirmada: <CheckCircle2 size={13} className="inline mr-1" />,
    Cancelada: <XCircle size={13} className="inline mr-1" />,
    Completada: <Clock size={13} className="inline mr-1" />,
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
      {icons[status]}{status}
    </span>
  );
};

const today = () => new Date().toISOString().split('T')[0];

export const ReservationsPage = () => {
  const [data, setData] = useState<ReservationListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [guests, setGuests] = useState<Guest[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    guest_id: '',
    room_id: '',
    check_in: today(),
    check_out: '',
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [resData, guestData, roomData] = await Promise.all([
        getReservations(),
        getGuests(1, 200, '', false),
        getRooms(0, 200),
      ]);
      setData(resData);
      setGuests(guestData.items.filter(g => g.is_active));
      setRooms(roomData.items.filter(r => r.is_active));
    } catch {
      toast.error('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const clearError = (field: string) =>
    setErrors(prev => { const n = { ...prev }; delete n[field]; return n; });

  const validate = () => {
    const e: Record<string, string> = {};
    if (!formData.guest_id) e.guest_id = 'Seleccione un huésped';
    if (!formData.room_id) e.room_id = 'Seleccione una habitación';
    if (!formData.check_in) e.check_in = 'La fecha de check-in es requerida';
    if (!formData.check_out) e.check_out = 'La fecha de check-out es requerida';
    else if (formData.check_out <= formData.check_in)
      e.check_out = 'El check-out debe ser posterior al check-in';
    const ci = new Date(formData.check_in);
    const todayDate = new Date(today());
    if (ci < todayDate) e.check_in = 'No se permiten fechas pasadas';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleOpenModal = () => {
    setErrors({});
    setFormData({ guest_id: '', room_id: '', check_in: today(), check_out: '', notes: '' });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    try {
      await createReservation(formData);
      toast.success('Reserva creada exitosamente');
      setIsModalOpen(false);
      fetchAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al crear la reserva');
    }
  };

  const handleCancel = async (r: Reservation) => {
    if (!confirm(`¿Cancelar reserva #${r.id.slice(-6).toUpperCase()}?`)) return;
    try {
      await cancelReservation(r.id);
      toast.success('Reserva cancelada');
      fetchAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al cancelar');
    }
  };

  const handleComplete = async (r: Reservation) => {
    if (!confirm(`¿Marcar como completada la reserva #${r.id.slice(-6).toUpperCase()}?`)) return;
    try {
      await completeReservation(r.id);
      toast.success('Reserva completada (check-out registrado)');
      fetchAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al completar');
    }
  };

  const getGuestName = (id: string) => {
    const g = guests.find(x => x.id === id);
    return g ? `${g.first_name} ${g.last_name}` : id.slice(-6);
  };

  const getRoomNumber = (id: string) => {
    const r = rooms.find(x => x.id === id);
    return r ? `Hab. ${r.number} (${r.room_type})` : id.slice(-6);
  };

  const inputClass = (field: string) =>
    `w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${
      errors[field] ? 'border-red-500' : 'border-stone-300'
    }`;

  // Summary counts
  const confirmadas = data?.items.filter(r => r.status === 'Confirmada').length ?? 0;
  const canceladas = data?.items.filter(r => r.status === 'Cancelada').length ?? 0;
  const completadas = data?.items.filter(r => r.status === 'Completada').length ?? 0;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-serif text-stone-900">Reservas</h1>
          <p className="text-sm text-stone-500 mt-1">Control de disponibilidad y estadías</p>
        </div>
        <button
          onClick={handleOpenModal}
          className="flex items-center gap-2 bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-900 transition-colors"
        >
          <Plus size={20} /> Nueva Reserva
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <p className="text-sm font-medium text-stone-600">Confirmadas</p>
          <p className="text-3xl font-bold text-stone-800 mt-1">{confirmadas}</p>
        </div>
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-4">
          <p className="text-sm font-medium text-stone-600">Completadas</p>
          <p className="text-3xl font-bold text-stone-800 mt-1">{completadas}</p>
        </div>
        <div className="rounded-xl border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-stone-600">Canceladas</p>
          <p className="text-3xl font-bold text-stone-800 mt-1">{canceladas}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-stone-500">Cargando reservas...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[900px]">
              <thead>
                <tr className="bg-stone-100 border-b border-stone-200 text-stone-600 text-sm">
                  <th className="px-6 py-4 font-medium">ID</th>
                  <th className="px-6 py-4 font-medium">Huésped</th>
                  <th className="px-6 py-4 font-medium">Habitación</th>
                  <th className="px-6 py-4 font-medium">Check-in</th>
                  <th className="px-6 py-4 font-medium">Check-out</th>
                  <th className="px-6 py-4 font-medium">Total</th>
                  <th className="px-6 py-4 font-medium">Estado</th>
                  <th className="px-6 py-4 font-medium text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map(r => (
                  <tr key={r.id} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
                    <td className="px-6 py-4 text-xs font-mono text-stone-400">#{r.id.slice(-6).toUpperCase()}</td>
                    <td className="px-6 py-4 text-stone-800 font-medium">{getGuestName(r.guest_id)}</td>
                    <td className="px-6 py-4 text-stone-600">{getRoomNumber(r.room_id)}</td>
                    <td className="px-6 py-4 text-stone-600">{r.check_in}</td>
                    <td className="px-6 py-4 text-stone-600">{r.check_out}</td>
                    <td className="px-6 py-4 font-medium text-stone-800">
                      {clp(r.total_price)}
                    </td>
                    <td className="px-6 py-4">{statusBadge(r.status)}</td>
                    <td className="px-6 py-4 text-right">
                      {r.status === 'Confirmada' && (
                        <div className="flex justify-end gap-1">
                          <button
                            title="Completar (Check-out)"
                            onClick={() => handleComplete(r)}
                            className="text-emerald-400 hover:text-emerald-700 p-1 transition-colors"
                          >
                            <CheckCircle2 size={18} />
                          </button>
                          <button
                            title="Cancelar"
                            onClick={() => handleCancel(r)}
                            className="text-red-300 hover:text-red-600 p-1 transition-colors"
                          >
                            <XCircle size={18} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr>
                    <td colSpan={8} className="px-6 py-8 text-center text-stone-500">
                      No hay reservas registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Nueva Reserva */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Nueva Reserva">
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Huésped</label>
            <select
              value={formData.guest_id}
              onChange={e => { setFormData({ ...formData, guest_id: e.target.value }); clearError('guest_id'); }}
              className={inputClass('guest_id')}
            >
              <option value="">— Seleccione un huésped —</option>
              {guests.map(g => (
                <option key={g.id} value={g.id}>{g.first_name} {g.last_name} · {g.document_number}</option>
              ))}
            </select>
            {errors.guest_id && <p className="text-red-500 text-xs mt-1">{errors.guest_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Habitación</label>
            <select
              value={formData.room_id}
              onChange={e => { setFormData({ ...formData, room_id: e.target.value }); clearError('room_id'); }}
              className={inputClass('room_id')}
            >
              <option value="">— Seleccione una habitación —</option>
              {rooms.map(r => (
                <option key={r.id} value={r.id} disabled={r.state === 'Mantenimiento'}>
                  Hab. {r.number} — {r.room_type} — {r.state} — {clp(r.price_per_night)}/noche
                </option>
              ))}
            </select>
            {errors.room_id && <p className="text-red-500 text-xs mt-1">{errors.room_id}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Check-in</label>
              <input
                type="date"
                value={formData.check_in}
                min={today()}
                onChange={e => { setFormData({ ...formData, check_in: e.target.value }); clearError('check_in'); }}
                className={inputClass('check_in')}
              />
              {errors.check_in && <p className="text-red-500 text-xs mt-1">{errors.check_in}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Check-out</label>
              <input
                type="date"
                value={formData.check_out}
                min={formData.check_in || today()}
                onChange={e => { setFormData({ ...formData, check_out: e.target.value }); clearError('check_out'); }}
                className={inputClass('check_out')}
              />
              {errors.check_out && <p className="text-red-500 text-xs mt-1">{errors.check_out}</p>}
            </div>
          </div>

          {/* Price preview */}
          {formData.room_id && formData.check_in && formData.check_out && formData.check_out > formData.check_in && (() => {
            const room = rooms.find(r => r.id === formData.room_id);
            const nights = (new Date(formData.check_out).getTime() - new Date(formData.check_in).getTime()) / 86400000;
            const total = room ? nights * room.price_per_night : 0;
            return (
              <div className="bg-stone-50 border border-stone-200 rounded-lg p-3 text-sm text-stone-600">
                <span className="font-medium">{nights} noche(s)</span> ×{' '}
                <span>{clp(room?.price_per_night ?? 0)}/noche</span>
                {' = '}
                <span className="font-bold text-stone-900">{clp(total)}</span>
              </div>
            );
          })()}

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Notas (opcional)</label>
            <textarea
              value={formData.notes}
              onChange={e => setFormData({ ...formData, notes: e.target.value })}
              className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200 h-20 resize-none"
              placeholder="Peticiones especiales, etc."
            />
          </div>

          <div className="pt-4 flex justify-end gap-3 border-t border-stone-200 mt-6">
            <button type="button" onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-md transition-colors">
              Cancelar
            </button>
            <button type="submit"
              className="px-4 py-2 bg-stone-800 text-white rounded-md hover:bg-stone-900 transition-colors">
              Confirmar Reserva
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
