import { useState, useEffect } from 'react';
import type { ReactElement } from 'react';
import { getDashboardStats } from '../api/dashboard';
import type { DashboardStats } from '../api/dashboard';
import {
  Users, BedDouble, CalendarCheck, TrendingUp,
  UserCheck, CheckCircle2, XCircle, Clock,
  BedSingle, Hotel, Star, Crown,
} from 'lucide-react';

// ── Helpers ───────────────────────────────────────────────────────────────────

const clp = (n: number) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n);

const pct = (part: number, total: number) =>
  total === 0 ? 0 : Math.round((part / total) * 100);

const ROOM_TYPE_COLORS: Record<string, string> = {
  Simple: 'from-blue-400 to-blue-600',
  Doble: 'from-emerald-400 to-emerald-600',
  Suite: 'from-amber-400 to-amber-600',
  Presidencial: 'from-purple-400 to-purple-700',
};

const ROOM_TYPE_ICONS: Record<string, ReactElement> = {
  Simple: <BedSingle size={20} />,
  Doble: <BedDouble size={20} />,
  Suite: <Star size={20} />,
  Presidencial: <Crown size={20} />,
};

// ── Componentes auxiliares ────────────────────────────────────────────────────

interface StatCardProps {
  icon: ReactElement;
  label: string;
  value: string | number;
  sub?: string;
  gradient?: string;
}
const StatCard = ({ icon, label, value, sub, gradient = 'from-stone-700 to-stone-900' }: StatCardProps) => (
  <div className={`bg-gradient-to-br ${gradient} rounded-2xl p-6 text-white shadow-lg`}>
    <div className="flex justify-between items-start">
      <div>
        <p className="text-white/70 text-sm font-medium tracking-wide uppercase">{label}</p>
        <p className="text-4xl font-bold mt-2">{value}</p>
        {sub && <p className="text-white/60 text-xs mt-1">{sub}</p>}
      </div>
      <div className="bg-white/20 rounded-xl p-3">{icon}</div>
    </div>
  </div>
);

interface OccupancyBarProps {
  available: number;
  occupied: number;
  maintenance: number;
  total: number;
}
const OccupancyBar = ({ available, occupied, maintenance, total }: OccupancyBarProps) => {
  const avPct = pct(available, total);
  const occPct = pct(occupied, total);
  const mntPct = pct(maintenance, total);
  return (
    <div className="w-full h-2 rounded-full overflow-hidden bg-stone-100 flex">
      <div className="bg-emerald-400 h-full transition-all" style={{ width: `${avPct}%` }} title={`Disponible: ${available}`} />
      <div className="bg-amber-400 h-full transition-all" style={{ width: `${occPct}%` }} title={`Ocupada: ${occupied}`} />
      <div className="bg-red-400 h-full transition-all" style={{ width: `${mntPct}%` }} title={`Mantenimiento: ${maintenance}`} />
    </div>
  );
};

// ── Dashboard ─────────────────────────────────────────────────────────────────

export const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch(() => {/* silent */})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-stone-800" />
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-8 text-stone-500">No se pudieron cargar las estadísticas.</div>
    );
  }

  const { guests, rooms, reservations, revenue } = stats;
  const occupancyRate = pct(rooms.ocupada, rooms.total);

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-serif text-stone-900">Panel de Control</h1>
        <p className="text-stone-500 text-sm mt-1">Resumen operacional en tiempo real — Descanso Premium</p>
      </div>

      {/* ── KPI Cards ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          icon={<UserCheck size={22} />}
          label="Huéspedes en el Hotel"
          value={guests.currently_in_hotel}
          sub={`de ${guests.total_active} registrados`}
          gradient="from-stone-700 to-stone-900"
        />
        <StatCard
          icon={<BedDouble size={22} />}
          label="Ocupación Actual"
          value={`${occupancyRate}%`}
          sub={`${rooms.ocupada} de ${rooms.total} habitaciones`}
          gradient="from-amber-500 to-amber-700"
        />
        <StatCard
          icon={<CalendarCheck size={22} />}
          label="Reservas Confirmadas"
          value={reservations.confirmada}
          sub={`${reservations.total} reservas en total`}
          gradient="from-emerald-500 to-emerald-700"
        />
        <StatCard
          icon={<TrendingUp size={22} />}
          label="Ingresos Históricos"
          value={clp(revenue.historical_total_clp)}
          sub={`${clp(revenue.confirmed_total_clp)} confirmados`}
          gradient="from-indigo-500 to-indigo-700"
        />
      </div>

      {/* ── Segunda fila: Habitaciones + Reservas ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Estado de Habitaciones */}
        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-6">
          <h2 className="text-lg font-semibold text-stone-800 mb-5">Estado de Habitaciones</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="text-sm text-stone-600">Disponibles</span>
              </div>
              <div className="text-right">
                <span className="font-bold text-stone-800">{rooms.disponible}</span>
                <span className="text-xs text-stone-400 ml-1">({pct(rooms.disponible, rooms.total)}%)</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <span className="text-sm text-stone-600">Ocupadas</span>
              </div>
              <div className="text-right">
                <span className="font-bold text-stone-800">{rooms.ocupada}</span>
                <span className="text-xs text-stone-400 ml-1">({pct(rooms.ocupada, rooms.total)}%)</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <span className="text-sm text-stone-600">Mantenimiento</span>
              </div>
              <div className="text-right">
                <span className="font-bold text-stone-800">{rooms.mantenimiento}</span>
                <span className="text-xs text-stone-400 ml-1">({pct(rooms.mantenimiento, rooms.total)}%)</span>
              </div>
            </div>
            <div className="pt-2">
              <OccupancyBar
                available={rooms.disponible}
                occupied={rooms.ocupada}
                maintenance={rooms.mantenimiento}
                total={rooms.total}
              />
            </div>
            <p className="text-xs text-stone-400 text-center pt-1">Total: {rooms.total} habitaciones activas</p>
          </div>
        </div>

        {/* Estado de Reservas */}
        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-6">
          <h2 className="text-lg font-semibold text-stone-800 mb-5">Estado de Reservas</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-500" />
                <span className="text-sm text-stone-600">Confirmadas</span>
              </div>
              <span className="font-bold text-stone-800">{reservations.confirmada}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-stone-400" />
                <span className="text-sm text-stone-600">Completadas</span>
              </div>
              <span className="font-bold text-stone-800">{reservations.completada}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <XCircle size={16} className="text-red-400" />
                <span className="text-sm text-stone-600">Canceladas</span>
              </div>
              <span className="font-bold text-stone-800">{reservations.cancelada}</span>
            </div>
            <div className="border-t border-stone-100 pt-3 mt-2">
              <div className="flex justify-between text-xs text-stone-500">
                <span>Total reservas</span>
                <span className="font-bold text-stone-700">{reservations.total}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Resumen de Ingresos */}
        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-6">
          <h2 className="text-lg font-semibold text-stone-800 mb-5">Ingresos (CLP)</h2>
          <div className="space-y-4">
            <div className="bg-emerald-50 rounded-xl p-4">
              <p className="text-xs text-stone-500 font-medium uppercase tracking-wide">Confirmados (vigentes)</p>
              <p className="text-2xl font-bold text-emerald-700 mt-1 break-all">
                {clp(revenue.confirmed_total_clp)}
              </p>
            </div>
            <div className="bg-indigo-50 rounded-xl p-4">
              <p className="text-xs text-stone-500 font-medium uppercase tracking-wide">Histórico total</p>
              <p className="text-2xl font-bold text-indigo-700 mt-1 break-all">
                {clp(revenue.historical_total_clp)}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Users size={14} className="text-stone-400" />
              <span className="text-sm text-stone-500">
                {guests.total_active} huéspedes registrados
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Desglose por tipo de habitación ───────────────────────────────── */}
      <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-6">
        <h2 className="text-lg font-semibold text-stone-800 mb-6">Detalle por Tipo de Habitación</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(rooms.by_type).map(([type, typeStats]) => (
            <div key={type} className="rounded-xl overflow-hidden border border-stone-100 shadow-sm">
              {/* Header colorido */}
              <div className={`bg-gradient-to-r ${ROOM_TYPE_COLORS[type] ?? 'from-stone-400 to-stone-600'} p-4 text-white`}>
                <div className="flex justify-between items-center">
                  {ROOM_TYPE_ICONS[type] ?? <Hotel size={20} />}
                  <span className="text-2xl font-bold">{typeStats.total}</span>
                </div>
                <p className="text-sm font-semibold mt-1">{type}</p>
              </div>
              {/* Detalle */}
              <div className="p-3 space-y-2 bg-stone-50 text-xs text-stone-600">
                <div className="flex justify-between">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
                    Disponibles
                  </span>
                  <span className="font-bold text-stone-800">{typeStats.disponible}</span>
                </div>
                <div className="flex justify-between">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
                    Ocupadas
                  </span>
                  <span className="font-bold text-stone-800">{typeStats.ocupada}</span>
                </div>
                <div className="flex justify-between">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
                    Mant.
                  </span>
                  <span className="font-bold text-stone-800">{typeStats.mantenimiento}</span>
                </div>
                <div className="pt-1">
                  <OccupancyBar
                    available={typeStats.disponible}
                    occupied={typeStats.ocupada}
                    maintenance={typeStats.mantenimiento}
                    total={typeStats.total}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
