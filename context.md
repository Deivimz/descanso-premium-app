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

<!-- Los pasos siguientes se añadirán aquí conforme avancemos -->

