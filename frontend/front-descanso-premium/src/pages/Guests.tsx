import { useState, useEffect } from 'react';
import { getGuests, createGuest, updateGuest, deleteGuest } from '../api/guests';
import type { Guest, GuestListResponse } from '../api/guests';
import { Modal } from '../components/Modal';
import { Plus, Pencil, Trash2, Search } from 'lucide-react';
import { toast } from 'react-toastify';
import { validateRut, formatRut } from '../utils/validators';

export const Guests = () => {
  const [data, setData] = useState<GuestListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGuest, setEditingGuest] = useState<Guest | null>(null);
  
  // Form State
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    document_type: 'RUT',
    document_number: '',
    nationality: '',
    address: '',
    notes: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Borra el mensaje de un campo cuando el usuario lo corrige
  const clearError = (field: string) =>
    setErrors(prev => { const next = { ...prev }; delete next[field]; return next; });

  const fetchGuests = async (p = page, search = searchQuery) => {
    setLoading(true);
    try {
      const response = await getGuests(p, 10, search);
      setData(response);
    } catch (error) {
      console.error("Error fetching guests", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuests();
  }, [page]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchGuests(1, searchQuery);
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.first_name.trim() || formData.first_name.length < 2) {
      newErrors.first_name = 'El nombre debe tener al menos 2 caracteres';
    }
    if (!formData.last_name.trim() || formData.last_name.length < 2) {
      newErrors.last_name = 'El apellido debe tener al menos 2 caracteres';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }
    if (!formData.document_number.trim()) {
      newErrors.document_number = 'El documento es requerido';
    } else if (formData.document_type === 'RUT' && !validateRut(formData.document_number)) {
      newErrors.document_number = 'RUT inválido';
    } else if (formData.document_number.length < 5) {
      newErrors.document_number = 'El documento debe tener al menos 5 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOpenModal = (guest?: Guest) => {
    setErrors({});
    if (guest) {
      setEditingGuest(guest);
      setFormData({
        first_name: guest.first_name,
        last_name: guest.last_name,
        email: guest.email,
        phone: guest.phone || '',
        document_type: guest.document_type,
        document_number: guest.document_number,
        nationality: guest.nationality || '',
        address: guest.address || '',
        notes: guest.notes || ''
      });
    } else {
      setEditingGuest(null);
      setFormData({ 
        first_name: '', last_name: '', email: '', phone: '', 
        document_type: 'RUT', document_number: '', nationality: '', address: '', notes: '' 
      });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      if (editingGuest) {
        await updateGuest(editingGuest.id, formData);
        toast.success('Huésped actualizado exitosamente');
      } else {
        await createGuest(formData);
        toast.success('Huésped registrado exitosamente');
      }
      setIsModalOpen(false);
      fetchGuests();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al guardar el huésped');
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('¿Está seguro de eliminar a este huésped?')) {
      try {
        await deleteGuest(id);
        toast.success('Huésped eliminado exitosamente');
        fetchGuests();
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Error al eliminar el huésped');
      }
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-serif text-stone-900">Directorio de Huéspedes</h1>
        <button 
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-900 transition-colors"
        >
          <Plus size={20} /> Nuevo Huésped
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
        <div className="p-4 border-b border-stone-200 bg-stone-50">
          <form onSubmit={handleSearch} className="flex gap-2 w-full max-w-md relative">
            <input 
              type="text" 
              placeholder="Buscar por nombre, email o documento..." 
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
            />
            <Search size={18} className="absolute left-3 top-3 text-stone-400" />
            <button type="submit" className="px-4 py-2 bg-stone-200 text-stone-700 rounded-md hover:bg-stone-300 transition-colors">
              Buscar
            </button>
          </form>
        </div>

        {loading ? (
          <div className="p-8 text-center text-stone-500">Cargando directorio...</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[800px]">
                <thead>
                  <tr className="bg-stone-100 border-b border-stone-200 text-stone-600 text-sm">
                    <th className="px-6 py-4 font-medium">Nombre Completo</th>
                    <th className="px-6 py-4 font-medium">Documento</th>
                    <th className="px-6 py-4 font-medium">Contacto</th>
                    <th className="px-6 py-4 font-medium">Nacionalidad</th>
                    <th className="px-6 py-4 font-medium text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.items.map(g => (
                    <tr key={g.id} className={`border-b border-stone-100 hover:bg-stone-50 transition-colors ${!g.is_active ? 'opacity-50' : ''}`}>
                      <td className="px-6 py-4">
                        <p className="text-stone-800 font-medium">{g.first_name} {g.last_name}</p>
                        {!g.is_active && <span className="text-xs text-red-500 font-semibold uppercase">Inactivo</span>}
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-stone-800 font-medium">{g.document_number}</p>
                        <p className="text-xs text-stone-500">{g.document_type}</p>
                      </td>
                      <td className="px-6 py-4 text-stone-600">
                        <p>{g.email}</p>
                        <p className="text-xs">{g.phone}</p>
                      </td>
                      <td className="px-6 py-4 text-stone-600">{g.nationality || '-'}</td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => handleOpenModal(g)} className="text-stone-500 hover:text-stone-800 mr-3 p-1">
                          <Pencil size={18} />
                        </button>
                        {g.is_active && (
                          <button onClick={() => handleDelete(g.id)} className="text-red-400 hover:text-red-600 p-1">
                            <Trash2 size={18} />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {(!data?.items || data.items.length === 0) && (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-stone-500">No se encontraron huéspedes.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            
            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="px-6 py-4 border-t border-stone-200 flex items-center justify-between bg-stone-50">
                <span className="text-sm text-stone-500">
                  Mostrando página {data.page} de {data.pages} ({data.total} en total)
                </span>
                <div className="flex gap-2">
                  <button 
                    disabled={data.page === 1}
                    onClick={() => setPage(p => p - 1)}
                    className="px-3 py-1 border border-stone-300 rounded-md disabled:opacity-50 text-stone-600 hover:bg-stone-200 transition-colors"
                  >
                    Anterior
                  </button>
                  <button 
                    disabled={data.page === data.pages}
                    onClick={() => setPage(p => p + 1)}
                    className="px-3 py-1 border border-stone-300 rounded-md disabled:opacity-50 text-stone-600 hover:bg-stone-200 transition-colors"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        title={editingGuest ? 'Editar Huésped' : 'Registrar Nuevo Huésped'}
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
              <label className="block text-sm font-medium text-stone-700 mb-1">Tipo de Documento</label>
              <select 
                value={formData.document_type} 
                onChange={e => {
                  const type = e.target.value;
                  setFormData({...formData, document_type: type, document_number: type === 'RUT' ? formatRut(formData.document_number) : formData.document_number});
                }}
                className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
              >
                <option value="RUT">RUT</option>
                <option value="PASAPORTE">Pasaporte</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Número de Documento</label>
              <input 
                type="text" 
                value={formData.document_number}
                placeholder={formData.document_type === 'RUT' ? '12.345.678-5' : 'Número de pasaporte'}
                onChange={e => {
                  const val = formData.document_type === 'RUT' ? formatRut(e.target.value) : e.target.value;
                  setFormData({...formData, document_number: val});
                  clearError('document_number');
                }}
                className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.document_number ? 'border-red-500' : 'border-stone-300'}`}
              />
              {errors.document_number && <p className="text-red-500 text-xs mt-1">{errors.document_number}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Correo Electrónico</label>
              <input 
                type="email" 
                value={formData.email} 
                onChange={e => { setFormData({...formData, email: e.target.value}); clearError('email'); }}
                className={`w-full p-2 border rounded-md outline-none focus:ring-2 focus:ring-stone-200 ${errors.email ? 'border-red-500' : 'border-stone-300'}`}
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Teléfono</label>
              <input 
                type="text" 
                value={formData.phone} 
                onChange={e => setFormData({...formData, phone: e.target.value})}
                className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Nacionalidad</label>
            <input 
              type="text" 
              value={formData.nationality} 
              onChange={e => setFormData({...formData, nationality: e.target.value})}
              className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Dirección</label>
            <input 
              type="text" 
              value={formData.address} 
              onChange={e => setFormData({...formData, address: e.target.value})}
              className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Notas u Observaciones</label>
            <textarea 
              value={formData.notes} 
              onChange={e => setFormData({...formData, notes: e.target.value})}
              className="w-full p-2 border border-stone-300 rounded-md outline-none focus:ring-2 focus:ring-stone-200 h-24 resize-none"
            ></textarea>
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
              Guardar Huésped
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
