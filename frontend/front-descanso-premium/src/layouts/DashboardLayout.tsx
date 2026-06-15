import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Building2, Key, Users, LayoutDashboard, LogOut } from 'lucide-react';

export const DashboardLayout = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
      isActive 
        ? 'bg-stone-800 text-stone-100 font-medium shadow-md' 
        : 'text-stone-600 hover:bg-stone-200 hover:text-stone-900'
    }`;

  return (
    <div className="min-h-screen flex bg-[#F7F5F0]">
      {/* Sidebar - Vintage Style */}
      <aside className="w-64 bg-[#EBE7DF] border-r border-stone-300 flex flex-col shadow-sm relative z-10">
        <div className="p-6 text-center border-b border-stone-300">
          <h1 className="text-2xl font-serif text-stone-900 tracking-tight">Descanso<br/>Premium</h1>
          <p className="text-xs text-stone-500 mt-2 tracking-widest uppercase font-semibold">Management</p>
        </div>
        
        <nav className="flex-1 px-4 py-6 flex flex-col gap-2">
          <NavLink to="/" className={navItemClass} end>
            <LayoutDashboard size={20} /> Dashboard
          </NavLink>
          <NavLink to="/guests" className={navItemClass}>
            <Users size={20} /> Huéspedes
          </NavLink>
          <NavLink to="/rooms" className={navItemClass}>
            <Key size={20} /> Habitaciones
          </NavLink>
          <NavLink to="/bookings" className={navItemClass}>
            <Building2 size={20} /> Reservas
          </NavLink>
          {user?.role === 'admin' && (
            <NavLink to="/users" className={navItemClass}>
              <Users size={20} /> Usuarios
            </NavLink>
          )}
        </nav>

        <div className="p-4 border-t border-stone-300">
          <div className="px-4 py-2 mb-4 bg-stone-200 rounded-lg text-sm text-stone-700">
            <p className="font-semibold text-stone-900">{user?.username}</p>
            <p className="text-xs">{user?.role}</p>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-4 py-2 text-stone-600 hover:text-red-700 hover:bg-red-50 transition-colors rounded-lg"
          >
            <LogOut size={18} /> Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};
