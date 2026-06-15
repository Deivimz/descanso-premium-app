import { useState, useEffect } from 'react';
import { getUsers, createUser, updateUser, deleteUser } from '../api/users';
import type { User } from '../store/authStore';
import { Modal } from '../components/Modal';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';
import { validateRut, formatRut } from '../utils/validators';

export const Users = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  
  // Form State
  const [formData, setFormData] = useState<{
    username: string;
    email: string;
    rut: string;
    first_name: string;
    last_name: string;
    password: string;
    role: 'admin' | 'staff';
    is_active: boolean;
  }>({
    username: '',
    email: '',
    rut: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'staff',
    is_active: true
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Borra el mensaje de un campo cuando el usuario lo corrige
  const clearError = (field: string) =>
    setErrors(prev => { const next = { ...prev }; delete next[field]; return next; });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (error) {
      console.error("Error fetching users", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.username.trim()) newErrors.username = 'El usuario es requerido';
    if (!formData.first_name.trim()) newErrors.first_name = 'El nombre es requerido';
    if (!formData.last_name.trim()) newErrors.last_name = 'El apellido es requerido';
    
    if (!formData.rut.trim()) {
      newErrors.rut = 'El RUT es requerido';
    } else if (!validateRut(formData.rut)) {
      newErrors.rut = 'RUT inválido';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }
    
    if (!editingUser && (!formData.password || formData.password.length < 6)) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    } else if (editingUser && formData.password && formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOpenModal = (user?: User) => {
    setErrors({});
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        email: user.email,
        rut: user.rut,
        first_name: user.first_name,
        last_name: user.last_name,
        password: '',
        role: user.role,
        is_active: user.is_active
      });
    } else {
      setEditingUser(null);
      setFormData({ username: '', email: '', rut: '', first_name: '', last_name: '', password: '', role: 'staff', is_active: true });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      if (editingUser) {
        const payload = { ...formData };
        if (!payload.password) {
          delete (payload as any).password;
        }
        await updateUser(editingUser.id, payload);
        toast.success('Usuario actualizado exitosamente');
      } else {
        await createUser(formData);
        toast.success('Usuario registrado exitosamente');
      }
      setIsModalOpen(false);
      fetchUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al guardar el usuario');
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('¿Está seguro de eliminar este usuario?')) {
      try {
        await deleteUser(id);
        toast.success('Usuario eliminado exitosamente');
        fetchUsers();
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Error al eliminar');
      }
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-serif text-stone-900">Mantenimiento de Usuarios</h1>
        <button 
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-900 transition-colors"
        >
          <Plus size={20} /> Nuevo Usuario
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-stone-500">Cargando...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-stone-100 border-b border-stone-200 text-stone-600 text-sm">
                <th className="px-6 py-4 font-medium">Nombre Completo</th>
                <th className="px-6 py-4 font-medium">RUT</th>
                <th className="px-6 py-4 font-medium">Usuario</th>
                <th className="px-6 py-4 font-medium">Email</th>
                <th className="px-6 py-4 font-medium">Rol</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
                  <td className="px-6 py-4 text-stone-800 font-medium">{u.first_name} {u.last_name}</td>
                  <td className="px-6 py-4 text-stone-600 font-medium">{u.rut}</td>
                  <td className="px-6 py-4 text-stone-600">{u.username}</td>
                  <td className="px-6 py-4 text-stone-600">{u.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${u.role === 'admin' ? 'bg-amber-100 text-amber-800' : 'bg-stone-200 text-stone-700'}`}>
                      {u.role.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {u.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => handleOpenModal(u)} className="text-stone-500 hover:text-stone-800 mr-3 p-1">
                      <Pencil size={18} />
                    </button>
                    <button onClick={() => handleDelete(u.id)} className="text-red-400 hover:text-red-600 p-1">
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-stone-500">No hay usuarios registrados.</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        title={editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
      >
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Nombre</label>
              <input 
                type="text" 
                value={formData.first_name} 
                onChange={e => { setFormData({...formData, first_name: e.target.value}); clearError('first_name'); }}
                className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.first_name ? 'border-red-500' : 'border-stone-300'}`}
              />
              {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Apellido</label>
              <input 
                type="text" 
                value={formData.last_name} 
                onChange={e => { setFormData({...formData, last_name: e.target.value}); clearError('last_name'); }}
                className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.last_name ? 'border-red-500' : 'border-stone-300'}`}
              />
              {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">RUT</label>
              <input 
                type="text" 
                value={formData.rut}
                placeholder="12.345.678-5"
                onChange={e => { setFormData({...formData, rut: formatRut(e.target.value)}); clearError('rut'); }}
                className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.rut ? 'border-red-500' : 'border-stone-300'}`}
              />
              {errors.rut && <p className="text-red-500 text-xs mt-1">{errors.rut}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Usuario</label>
              <input 
                type="text" 
                value={formData.username} 
                onChange={e => { setFormData({...formData, username: e.target.value}); clearError('username'); }}
                className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.username ? 'border-red-500' : 'border-stone-300'}`}
              />
              {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Email</label>
            <input 
              type="email" 
              value={formData.email} 
              onChange={e => { setFormData({...formData, email: e.target.value}); clearError('email'); }}
              className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.email ? 'border-red-500' : 'border-stone-300'}`}
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Contraseña {editingUser && <span className="text-stone-400 text-xs font-normal">(Dejar en blanco para no cambiar)</span>}
            </label>
            <input 
              type="password" 
              value={formData.password} 
              onChange={e => { setFormData({...formData, password: e.target.value}); clearError('password'); }}
              className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.password ? 'border-red-500' : 'border-stone-300'}`}
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Rol</label>
              <select 
                value={formData.role} 
                onChange={e => setFormData({...formData, role: e.target.value as 'admin' | 'staff'})}
                className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
              >
                <option value="staff">Staff</option>
                <option value="admin">Administrador</option>
              </select>
            </div>
            
            <div className="flex items-center mt-6">
              <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-stone-700">
                <input 
                  type="checkbox" 
                  checked={formData.is_active} 
                  onChange={e => setFormData({...formData, is_active: e.target.checked})}
                  className="w-4 h-4 text-stone-800 rounded focus:ring-stone-800"
                />
                Usuario Activo
              </label>
            </div>
          </div>

          <div className="pt-4 flex justify-end gap-3 border-t border-stone-200 mt-6">
            <button 
              type="button" 
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-md transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              className="px-4 py-2 bg-stone-800 text-white rounded-md hover:bg-stone-900 transition-colors"
            >
              Guardar Usuario
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
