export const Dashboard = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-serif text-stone-900 mb-6">Dashboard</h1>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
        <p className="text-stone-600 text-lg">Bienvenido al portal de gestión de Descanso Premium.</p>
      </div>
    </div>
  );
};

export const Rooms = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-serif text-stone-900 mb-6">Gestión de Habitaciones</h1>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
        <p className="text-stone-600">Próximamente: CRUD de habitaciones (Paso 3).</p>
      </div>
    </div>
  );
};

export const Bookings = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-serif text-stone-900 mb-6">Reservas</h1>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
        <p className="text-stone-600">Próximamente: Calendario y gestión de reservas (Paso 3).</p>
      </div>
    </div>
  );
};

export const Users = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-serif text-stone-900 mb-6">Mantenimiento de Usuarios</h1>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
        <p className="text-stone-600">Aquí se consumirá el CRUD de /api/users implementado en el backend.</p>
      </div>
    </div>
  );
};
