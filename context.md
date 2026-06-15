# context.md — Bitácora del Proyecto: Descanso Premium

> **Propósito:** Registro continuo de decisiones técnicas, artefactos creados y comandos necesarios para ejecutar/probar cada módulo del sistema.

---

## Metadatos del Proyecto

| Campo             | Valor                                      |
|-------------------|--------------------------------------------|
| **Proyecto**      | Descanso Premium – Hotel Management System |
| **Inicio**        | 2026-06-02                                 |
| **Stack Backend** | Python 3.12 · FastAPI 0.111 · Motor 3.4   |
| **Base de Datos** | MongoDB 7.0                                |
| **Stack Frontend**| React (Vite) · Axios · React Router · TailwindCSS |
| **Infra**         | Docker · Docker Compose v3.9               |

---

## Estructura de Carpetas (estado actual)

```
descanso-premium/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Settings via pydantic-settings
│   │   │   └── database.py          # Beanie ODM: init_db / close_db / get_client
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   └── base_repository.py   # BaseRepository[T] genérico
│   │   ├── guests/                  # Módulo completo de Huéspedes
│   │   │   ├── __init__.py
│   │   │   ├── model.py             # Guest(Document) — Beanie
│   │   │   ├── schemas.py           # GuestCreate, GuestUpdate, GuestResponse, GuestListResponse
│   │   │   ├── repository.py        # GuestRepository(BaseRepository[Guest])
│   │   │   ├── service.py           # GuestService — lógica de negocio
│   │   │   └── router.py            # APIRouter prefijo: /api/guests
│   │   ├── rooms/                   # [FUTURO] — mismo patrón
│   │   ├── bookings/                # [FUTURO] — mismo patrón
│   │   └── main.py                  # FastAPI + lifespan Beanie + routers
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env
├── .gitignore
└── context.md
```

---

## Paso 1 — Setup e Infraestructura (Docker) y Bitácora

**Fecha:** 2026-06-02

### Qué se construyó

| Artefacto                        | Descripción                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| `backend/app/main.py`            | Aplicación FastAPI con endpoint `/ping` (health-check) y CORS configurado   |
| `backend/requirements.txt`       | Dependencias Python para todo el proyecto (incluidas las de pasos futuros)  |
| `backend/Dockerfile`             | Imagen Docker basada en `python:3.12-slim` con hot-reload via Uvicorn       |
| `docker-compose.yml`             | Orquestación de 2 servicios: `mongodb` y `backend`                          |
| `.env`                           | Variables de entorno para desarrollo local                                  |
| `.gitignore`                     | Excluye `.env`, `__pycache__`, `node_modules`, etc.                         |
| `context.md`                     | Este archivo — bitácora del proyecto                                        |

### Decisiones Técnicas Clave

1. **`python:3.12-slim`** como imagen base: reduce el tamaño del contenedor (~180 MB vs ~900 MB de la imagen estándar).

2. **Hot-reload en desarrollo**: el volumen `./backend/app:/app/app` en `docker-compose.yml` monta el código local dentro del contenedor. Uvicorn arranca con `--reload`, por lo que cualquier cambio en el código se refleja sin reconstruir la imagen.

3. **Health-check en MongoDB**: `docker-compose.yml` define un `healthcheck` para `mongodb`. El servicio `backend` usa `depends_on: condition: service_healthy`, garantizando que el backend no intente conectarse antes de que Mongo esté listo.

4. **Variables de entorno centralizadas en `.env`**: el `docker-compose.yml` las consume con la sintaxis `${VAR:-default}`. Esto permite sobrescribir valores sin modificar el compose file.

5. **CORS `allow_origins: ["*"]`**: configurado permisivo solo para desarrollo. Se restringirá al dominio del frontend en producción (Paso 6+).

6. **Dependencias "adelantadas"** en `requirements.txt`: se incluyen desde ya `motor`, `pydantic-settings`, `python-jose` y `passlib` para que la imagen Docker no tenga que reconstruirse en cada paso posterior.

### Comandos para ejecutar y probar

```bash
# 1. Situarse en la raíz del proyecto
cd descanso-premium

# 2. Levantar los servicios (primera vez, construye la imagen)
docker compose up --build

# 3. Verificar el health-check (en otra terminal o en el navegador)
curl http://localhost:8000/ping
# Respuesta esperada:
# {"status":"ok","service":"descanso-premium-api","environment":"development"}

# 4. Acceder a la documentación interactiva
# Swagger UI  ->  http://localhost:8000/docs
# ReDoc       ->  http://localhost:8000/redoc

# 5. Detener los servicios
docker compose down

# 6. Detener Y eliminar volúmenes (resetea la BD)
docker compose down -v
```

### Notas / Pendientes

- El endpoint `/ping` no verifica la conexión a MongoDB (eso se hará en el Paso 2 con Motor).
- La variable `SECRET_KEY` ya está preparada en `.env` para el sistema JWT del Paso 5.

---

---

## Paso 2 — Configuración ODM (Beanie) y Prueba de Conexión

**Fecha:** 2026-06-02

### Qué se construyó

| Artefacto                      | Descripción                                                                                         |
|--------------------------------|-----------------------------------------------------------------------------------------------------|
| `backend/app/core/config.py`   | Clase `Settings` (pydantic-settings) que lee el `.env` y expone `mongo_uri` como propiedad          |
| `backend/app/core/database.py` | Inicialización de **Beanie ODM**: `init_db()` / `close_db()` / `get_client()`                       |
| `backend/app/main.py`          | Lifespan con Beanie + endpoint `/db-test` que verifica conectividad real con MongoDB                 |
| `requirements.txt`             | Agregado `beanie==1.26.0`                                                                            |

> Los schemas Pydantic previos fueron eliminados; los modelos Beanie se crearán a partir del Paso 2 continuación.

### Decisiones Técnicas Clave

1. **Beanie como ODM**: se eligió Beanie sobre Motor puro porque:
   - Los modelos son clases Python con validación Pydantic v2 integrada (`class Guest(Document)`).
   - CRUD expresivo sin queries en crudo (`await Guest.find_all().to_list()`).
   - Soporte nativo para índices únicos, referencias entre documentos y migraciones ligeras.
   - Construido sobre Motor → sigue siendo 100% async.

2. **`init_beanie(document_models=[...])`**: los modelos se inyectan desde `main.py` al llamar `init_db()`. Esto evita imports circulares (los modelos importan `database.py`, pero `database.py` no importa los modelos).

3. **`pydantic-settings`** para la configuración: la URI de MongoDB se construye como `@property` del objeto `Settings` para mantener un único punto de verdad.

4. **Endpoint `/db-test`**: ejecuta `admin.ping` + `list_collection_names()` + `server_info()` para una verificación completa con información útil (versión de Mongo, colecciones activas).

### Comandos para ejecutar y probar

```bash
# 1. Rebuild completo (instala beanie en la imagen)
docker compose up --build -d

# 2. Verificar la conexión con Beanie + MongoDB
# Respuesta esperada:
# {"status":"ok","database":"descanso_db","host":"mongodb","mongo_version":"7.0.x","collections":[],"ping_ok":true}
Invoke-WebRequest -Uri http://localhost:8000/db-test -UseBasicParsing | Select-Object -ExpandProperty Content

# 3. Ver logs del startup (confirmar Beanie inicializado)
docker compose logs backend --tail=15
# Línea esperada: "✅  Beanie inicializado — base de datos: 'descanso_db' | modelos: []"

# 4. Documentación interactiva
# http://localhost:8000/docs
```

### Notas / Pendientes

- `document_models = []` en `main.py` es temporal; se llenará con los modelos Beanie (`Guest`, `Room`, `Booking`) en la continuación del Paso 2.
- Las colecciones aparecerán vacías hasta que se inserte el primer documento.

---

<!-- Los pasos siguientes se añadirán aquí conforme avancemos -->


---

## Paso 2b — Módulo de Huéspedes (Arquitectura por Módulos)

**Fecha:** 2026-06-02

### Qué se construyó

| Artefacto | Descripción |
|---|---|
| `shared/base_repository.py` | `BaseRepository[T]` genérico: CRUD completo sobre cualquier Document Beanie |
| `guests/model.py` | `Guest(Document)` con índices únicos en email y document_number |
| `guests/schemas.py` | `GuestCreate`, `GuestUpdate`, `GuestResponse`, `GuestListResponse` |
| `guests/repository.py` | `GuestRepository`: búsqueda por email, documento y texto libre (regex) |
| `guests/service.py` | `GuestService`: validaciones de negocio, paginación, soft-delete |
| `guests/router.py` | 6 endpoints REST bajo `/api/guests` |
| `main.py` | Actualizado: registra `Guest` en Beanie e incluye `guests_router` |

### Decisiones Técnicas Clave

1. **Arquitectura por módulos (feature-based)**: cada entidad tiene su propia carpeta autocontenida (`guests/`). Agregar `rooms/` o `bookings/` solo requiere crear la misma estructura — `main.py` no necesita cambios estructurales, solo registrar el modelo y el router.

2. **`shared/base_repository.py`**: único código compartido entre módulos. Contiene `BaseRepository[T]` genérico con `create`, `find_by_id`, `find_all`, `count`, `update`, `soft_delete`, `hard_delete`.

3. **Soft-delete**: `DELETE /api/guests/{id}` establece `is_active=False`. El registro permanece en la BD para preservar el historial de reservas futuras. Parámetro `include_inactive=true` expone los inactivos.

4. **Estrategia de relaciones futuras**: `Guest` no referencia a `Booking` ni `Room`. Será `Booking` quien tenga `guest_id: PydanticObjectId` (FK en el lado "muchos"). El endpoint `GET /api/guests/{id}/bookings` ya existe y retorna `[]` hasta que `BookingRepository` sea implementado.

5. **`redirect_slashes=False`**: configurado en la app FastAPI para evitar `307 Temporary Redirect` que rompe clientes que no siguen redirects automáticamente (curl, fetch sin seguimiento, etc.).

### Endpoints del módulo Guests

| Método | Ruta | Descripción | HTTP OK |
|---|---|---|---|
| `POST` | `/api/guests` | Crear huésped | 201 |
| `GET` | `/api/guests` | Listar con paginación y búsqueda | 200 |
| `GET` | `/api/guests/{id}` | Obtener por ID | 200 |
| `PATCH` | `/api/guests/{id}` | Actualización parcial | 200 |
| `DELETE` | `/api/guests/{id}` | Soft-delete | 200 |
| `GET` | `/api/guests/{id}/bookings` | Reservas del huésped *(stub)* | 200 |

### Comandos para probar

```bash
# Crear huésped
curl -X POST http://localhost:8000/api/guests \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Maria","last_name":"Gonzalez","email":"maria@test.com","document_type":"DNI","document_number":"V-11111111"}'

# Listar
curl http://localhost:8000/api/guests

# Buscar
curl "http://localhost:8000/api/guests?search=Maria"

# Actualizar parcialmente
curl -X PATCH http://localhost:8000/api/guests/{id} \
  -H "Content-Type: application/json" \
  -d '{"phone":"+58 424 111 2233","notes":"VIP Gold"}'

# Soft-delete
curl -X DELETE http://localhost:8000/api/guests/{id}

# Ver inactivos
curl "http://localhost:8000/api/guests?include_inactive=true"

# Documentación interactiva
# http://localhost:8000/docs
```

### Notas / Pendientes

- `GET /api/guests/{id}/bookings` retorna `[]` hasta el Paso 3 (módulo Bookings).
- Los índices únicos de MongoDB se crean automáticamente al arrancar Beanie.
- El campo `document_number` se normaliza a mayúsculas en el validador de `GuestCreate`.

---

---

## Pasos 4 y 5 — Autenticación y Módulo de Usuarios (Backend)
## Pasos 7, 8 y 9 — Frontend: Estado, Rutas y UI Vintage Moderno

**Fecha:** 2026-06-14

### Qué se construyó

| Artefacto | Descripción |
|---|---|
| `backend/app/users/` | Módulo completo de Usuarios con Beanie (Model, Repo, Schemas, Router). |
| `backend/app/core/security.py` | Lógica de hasheo con `passlib` y JWT con `python-jose`. |
| `backend/app/core/dependencies.py` | `get_current_user` lee el JWT directamente de la cookie. |
| `backend/app/auth/router.py` | `POST /login` (set_cookie HttpOnly), `POST /logout` y `GET /me`. |
| `backend/app/main.py` | Se agregó una función de seed para crear el `admin` al inicio. |
| `frontend/.../vite.config.ts` | Proxy configurado hacia `http://localhost:8000/api`. |
| `frontend/.../api/axios.ts` | Instancia global de Axios con `withCredentials: true`. |
| `frontend/.../store/authStore.ts` | Estado global de autenticación con Zustand. |
| `frontend/.../App.tsx` | Rutas protegidas (`<PrivateRoute>`) implementadas con React Router. |
| `frontend/.../pages/` | `Login.tsx` (estilo vintage), `Views.tsx` (Placeholders) y `DashboardLayout`. |

### Decisiones Técnicas Clave

1. **Seguridad JWT via Cookies HttpOnly:** Se evitan ataques XSS ya que el JWT no es accesible desde el JavaScript del frontend. Las peticiones enviadas mediante Axios incluyen las cookies automáticamente por `withCredentials: true`.
2. **Seed de Admin:** Al arrancar la aplicación (`main.py`), si no existe el usuario `admin`, se crea con credenciales por defecto (`admin` / `admin123`) para permitir probar el sistema desde cero.
3. **Proxy en Vite:** Para solucionar los problemas de CORS y Cookies SameSite en el entorno local (localhost con diferentes puertos), Vite redirige las peticiones `/api` al backend transparente.
4. **UI Vintage Moderno:** Se incorporaron fuentes tipográficas elegantes (`Playfair Display` para títulos, `Inter` para texto base) con colores terracota/crema para darle una apariencia sofisticada al sistema, cumpliendo el requerimiento estético premium.

### Comandos para ejecutar y probar

```bash
# Frontend
npm run dev

# Credenciales por defecto creadas por el seed
# Usuario: admin
# Clave: admin123
```

<!-- Los pasos siguientes se añadirán aquí conforme avancemos -->

---

## Paso 6 — Frontend CRUD: Huéspedes y Usuarios

**Fecha:** 2026-06-14

### Qué se construyó

| Artefacto | Descripción |
|---|---|
| `frontend/.../api/guests.ts` | Integración Axios para CRUD de huéspedes. |
| `frontend/.../api/users.ts` | Integración Axios para CRUD de usuarios. |
| `frontend/.../components/Modal.tsx` | Componente UI genérico para formularios modales. |
| `frontend/.../pages/Guests.tsx` | Pantalla de mantenimiento de Huéspedes con validaciones strictas y tabla interactiva. |
| `frontend/.../pages/Users.tsx` | Pantalla de mantenimiento de Usuarios con control de contraseñas. |
| `frontend/.../App.tsx` | Rutas actualizadas para incluir `/guests`. |
| `frontend/.../layouts/DashboardLayout.tsx` | Se añadió "Huéspedes" al menú lateral (Sidebar). |

### Decisiones Técnicas Clave

1. **Modales para Formularios:** Se evitaron las navegaciones a sub-rutas `/new` o `/edit`. En su lugar, se implementaron ventanas modales en la misma página para mantener el flujo de trabajo ágil ("Vintage Moderno").
2. **Validaciones en React:** Para evitar recargar dependencias pesadas (como Zod o react-hook-form), las validaciones se manejaron directamente en el estado del componente (`validate()`), controlando expresiones regulares, longitudes mínimas y campos obligatorios.
3. **Soft-Delete Seguro:** En Huéspedes, los elementos inactivos se renderizan con opacidad reducida (`opacity-50`) en lugar de desaparecer por completo, permitiendo auditar la información. En Usuarios, se implementó eliminación física (hard delete) según la definición de la API.

---

## Paso 7 — Validación RUT (Módulo 11) y React-Toastify

**Fecha:** 2026-06-14

### Qué se construyó

| Artefacto | Descripción |
|---|---|
| `backend/app/shared/validators.py` | Implementación pura en Python del algoritmo Módulo 11 para validación de RUT Chileno. |
| `backend/app/users/model.py` | Se añadieron los campos `first_name`, `last_name`, `rut` (índice único), `created_at` y `updated_at` al modelo User. |
| `frontend/.../utils/validators.ts` | Funciones `validateRut` y `formatRut` en TypeScript. |
| `frontend/.../App.tsx` | Inclusión del `<ToastContainer />` para el sistema de notificaciones globales. |
| `frontend/.../pages/Users.tsx` y `Guests.tsx` | Validación del RUT y reemplazo de alertas nativas por `toast.success` y `toast.error`. |

### Decisiones Técnicas Clave

1. **Unificación de Validadores:** Tanto Huéspedes como Usuarios comparten la misma validación estricta de RUT en el Frontend y en el Backend, evitando que datos sucios lleguen a la base de datos.
2. **Formateo Dinámico UI:** Mientras el usuario teclea un RUT en los formularios de React, `formatRut` interviene para auto-agregar los puntos y el guión separador (`12.345.678-5`), lo que mejora ampliamente la UX (User Experience).
3. **Notificaciones UI:** Se reemplazó el uso obsoleto de `alert()` o el simple texto estático en rojo, por `react-toastify`, cumpliendo con el estándar de "Vintage Moderno" e interfaces fluidas propuesto al inicio del proyecto.
4. **Bug fix `updated_at`:** Se añadieron `created_at` y `updated_at` al modelo `User` para alinearlo con `BaseRepository`, que los actualiza automáticamente en cada `update()`/`soft_delete()`.

---

## Paso 8 — Módulos de Habitaciones y Reservas (Backend + Frontend)

**Fecha:** 2026-06-14

### Qué se construyó

#### Backend

| Artefacto | Descripción |
|---|---|
| `backend/app/rooms/model.py` | `Room(Document)` con enums `RoomType` (Simple/Doble/Suite/Presidencial) y `RoomState` (Disponible/Ocupada/Mantenimiento). Índices en `number` (único), `state` y `room_type`. |
| `backend/app/rooms/schemas.py` | `RoomCreate`, `RoomUpdate`, `RoomStateUpdate`, `RoomResponse`, `RoomListResponse`. |
| `backend/app/rooms/repository.py` | `RoomRepository`: `find_by_number`, `find_available`, `find_active`, `count_active`. |
| `backend/app/rooms/service.py` | Validación de número único, bloqueo de desactivación si la habitación está Ocupada. |
| `backend/app/rooms/router.py` | 5 endpoints bajo `/api/rooms`: GET lista, GET uno, POST, PATCH datos, PATCH estado, DELETE (soft). |
| `backend/app/reservations/model.py` | `Reservation(Document)` con `guest_id` y `room_id` como `PydanticObjectId` (referencias), y `check_in`/`check_out`/`status`/`total_price` embebidos. |
| `backend/app/reservations/schemas.py` | `ReservationCreate` con validador `check_out > check_in`, `ReservationUpdate`, `ReservationResponse`. |
| `backend/app/reservations/repository.py` | Consultas de solapamiento de fechas para habitación y huésped usando la fórmula `$lt`/`$gt`. |
| `backend/app/reservations/service.py` | Implementa las 3 reglas de negocio clave (ver abajo). |
| `backend/app/reservations/router.py` | 7 endpoints bajo `/api/reservations`: lista, historial por huésped, GET uno, POST, PATCH, cancel, complete. |
| `backend/app/main.py` | `Room` y `Reservation` registrados en Beanie; routers incluidos. |

#### Frontend

| Artefacto | Descripción |
|---|---|
| `frontend/.../api/rooms.ts` | Axios API: `getRooms`, `getRoom`, `createRoom`, `updateRoom`, `changeRoomState`, `deactivateRoom`. |
| `frontend/.../api/reservations.ts` | Axios API: `getReservations`, `getGuestReservations`, `createReservation`, `cancelReservation`, `completeReservation`. |
| `frontend/.../pages/Rooms.tsx` | Pantalla de Habitaciones con tarjetas de resumen por estado, tabla, modal de edición y modal de cambio de estado rápido. |
| `frontend/.../pages/Reservations.tsx` | Pantalla de Reservas con tarjetas de resumen, tabla completa, formulario modal con preview de precio calculado en tiempo real y acciones de Completar/Cancelar. |
| `frontend/.../App.tsx` | Rutas `/rooms` y `/bookings` actualizadas para usar los nuevos componentes reales. |

### Reglas de Negocio Implementadas (service.py)

| Regla | Descripción | Error HTTP |
|---|---|---|
| **Sin fechas pasadas** | `check_in` no puede ser anterior a la fecha de hoy | `422` |
| **No double-booking de habitación** | Una habitación no puede tener dos reservas `CONFIRMADA` en fechas solapadas | `409` |
| **Un huésped, una reserva activa** | Un huésped no puede tener dos reservas `CONFIRMADA` simultáneas | `409` |
| **Habitación en mantenimiento** | No se puede reservar una habitación en estado `Mantenimiento` | `409` |
| **No modificar completadas** | Una reserva `COMPLETADA` no puede ser modificada | `409` |

### Algoritmo de solapamiento de fechas

La condición utilizada para detectar conflictos entre dos rangos `[A_in, A_out)` y `[B_in, B_out)` es:
```
A_in < B_out  AND  A_out > B_in
```
Esto cubre todos los casos: contención, solapamiento izquierdo/derecho y equivalencia exacta.

### Endpoints del módulo Rooms

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/rooms` | Crear habitación |
| `GET` | `/api/rooms` | Listar (con filtro `only_available`) |
| `GET` | `/api/rooms/{id}` | Obtener por ID |
| `PATCH` | `/api/rooms/{id}` | Actualizar datos |
| `PATCH` | `/api/rooms/{id}/state` | Cambiar estado |
| `DELETE` | `/api/rooms/{id}` | Soft-delete |

### Endpoints del módulo Reservations

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/reservations` | Crear reserva (aplica las 3 reglas) |
| `GET` | `/api/reservations` | Listar todas |
| `GET` | `/api/reservations/guest/{guest_id}` | Historial del huésped |
| `GET` | `/api/reservations/{id}` | Obtener por ID |
| `PATCH` | `/api/reservations/{id}` | Actualizar estado/notas |
| `PATCH` | `/api/reservations/{id}/cancel` | Cancelar reserva |
| `PATCH` | `/api/reservations/{id}/complete` | Completar (check-out) |

### Estructura de Carpetas (estado actual)

```
descanso-premium/
├── backend/
│   └── app/
│       ├── core/           # config, database, dependencies, security
│       ├── shared/         # base_repository, validators
│       ├── auth/           # router JWT: login, logout, me
│       ├── users/          # CRUD de personal (admin/staff)
│       ├── guests/         # CRUD de huéspedes
│       ├── rooms/          # CRUD de habitaciones + gestión de estados ✅
│       ├── reservations/   # CRUD de reservas + validaciones de negocio ✅
│       └── main.py
└── frontend/
    └── front-descanso-premium/src/
        ├── api/            # axios.ts, guests.ts, users.ts, rooms.ts ✅, reservations.ts ✅
        ├── components/     # Modal, PrivateRoute
        ├── layouts/        # DashboardLayout (sidebar con 4 módulos)
        ├── pages/          # Login, Dashboard, Guests, Users, Rooms ✅, Reservations ✅
        └── store/          # authStore (Zustand)
```

