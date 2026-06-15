import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { KeyRound, Mail, Lock } from 'lucide-react';
import { toast } from 'react-toastify';

const isValidEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      toast.error('El correo electrónico es requerido');
      return;
    }
    if (!isValidEmail(email.trim())) {
      toast.error('Ingresa un correo electrónico válido');
      return;
    }
    if (!password.trim()) {
      toast.error('La contraseña es requerida');
      return;
    }

    try {
      await login(email.trim(), password);
      navigate('/');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Correo o contraseña incorrectos');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F5F0]">
      <div className="w-full max-w-md p-10 bg-white shadow-xl rounded-2xl border border-stone-200">
        <div className="text-center mb-10">
          <div className="mx-auto w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mb-4 text-stone-700 shadow-inner">
            <KeyRound size={32} />
          </div>
          <h1 className="text-4xl font-serif text-stone-900 mb-2">Descanso Premium</h1>
          <p className="text-sm text-stone-500 uppercase tracking-widest font-semibold">Staff Portal</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2" htmlFor="login-email">
              Correo Electrónico
            </label>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" />
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-stone-300 focus:border-stone-500 focus:ring-2 focus:ring-stone-200 transition-all outline-none bg-stone-50 text-stone-900"
                placeholder="correo@ejemplo.com"
                autoComplete="email"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2" htmlFor="login-password">
              Contraseña
            </label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" />
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-stone-300 focus:border-stone-500 focus:ring-2 focus:ring-stone-200 transition-all outline-none bg-stone-50 text-stone-900"
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-stone-800 hover:bg-stone-900 text-white font-medium rounded-lg shadow-md transition-colors focus:ring-4 focus:ring-stone-200 disabled:opacity-70 disabled:cursor-not-allowed mt-2"
          >
            {isLoading ? 'Iniciando sesión...' : 'Ingresar al Sistema'}
          </button>
        </form>

        <div className="mt-8 text-center text-xs text-stone-400">
          <p>&copy; {new Date().getFullYear()} Descanso Premium Hotels.</p>
        </div>
      </div>
    </div>
  );
};
