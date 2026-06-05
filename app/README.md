# RecipeVault — Backend (`app/`)

API REST construida con **FastAPI + Python 3.11**. Gestiona usuarios, recetas, inventario e imágenes, y se despliega en Azure App Service.

---

## Estructura de archivos

```
app/
├── app.py              # Punto de entrada: endpoints FastAPI, rate limiting, lifespan
├── database.py         # Toda la lógica de acceso a datos y lógica de negocio
├── db_models.py        # Modelos ORM SQLAlchemy (tablas de la base de datos)
├── models.py           # Esquemas Pydantic (validación de entrada y salida)
├── auth.py             # JWT: creación y validación de tokens, hash de contraseñas
├── storage.py          # Validación y subida de imágenes a Azure Blob Storage
├── requirements.txt    # Dependencias de producción
├── requirements-test.txt
├── frontend/           # Plantillas HTML y assets estáticos (ver frontend/README.md)
└── tests/              # Suite de tests (ver sección Tests más abajo)
```

---

## Módulos principales

### `app.py`
Punto de entrada de la aplicación. Define todos los endpoints HTTP y configura la infraestructura transversal:

- **Lifespan:** inicializa la base de datos al arrancar (`init_db()`). Si falla, la app no arranca.
- **Rate limiting** con `slowapi`: registro (5/min), login (10/min), recetas compartidas (30/min).
- **Logging:** tres niveles — `INFO` para operaciones normales, `WARNING` para accesos fallidos, `ERROR` para fallos críticos. Si `APPLICATIONINSIGHTS_CONNECTION_STRING` está configurado, los logs se envían a Azure Monitor vía OpenTelemetry.
- **Páginas HTML:** sirve las plantillas Jinja2 para todas las rutas de navegador (`/`, `/login`, `/recipes/{id}`, etc.).
- **API REST:** todos los endpoints bajo `/api/`.

### `database.py`
Contiene toda la lógica de negocio y acceso a datos. Los bloques principales son:

**Gestión del motor SQLAlchemy**
Inicialización lazy del engine y la sesión. Usa un context manager `_db()` que gestiona commit/rollback automáticamente.

**Asignación automática de imágenes**
`_pick_recipe_image()` busca palabras clave en el título, categoría e ingredientes de la receta y asigna una imagen de Unsplash representativa. Si no encuentra coincidencia, usa una imagen genérica.

**Conversión de unidades**
Sistema completo de conversión entre unidades de peso y volumen:
- `_normalize_unit()` — normaliza aliases ("gramos" → "g", "cucharada" → "cda", etc.)
- `_to_base()` — convierte cualquier cantidad a su unidad base (g para peso, ml para volumen)
- `_convert_between_units()` — compara cantidades en unidades distintas, incluyendo conversión masa↔volumen usando densidades aproximadas para ingredientes comunes (sal, harina, aceite, etc.)

**Lógica de stock bajo**
`_is_low_stock()` compara la cantidad actual de un ingrediente con su umbral mínimo usando el sistema de conversión de unidades, por lo que funciona correctamente aunque las unidades difieran (ej. stock en g, umbral en kg).

**Cocinar una receta**
`consume_ingredients_for_recipe()` es una operación atómica: si algún ingrediente falta o tiene stock insuficiente, no se descuenta ninguno. Solo cuando todos los ingredientes están disponibles se actualiza el inventario en la misma transacción.

**Seed de datos**
Al registrarse un nuevo usuario, se le crean automáticamente 5 recetas de ejemplo y 15 ingredientes de inventario para que la app no esté vacía en el primer acceso.

### `db_models.py`
Define las tres tablas con SQLAlchemy ORM:

| Tabla | Descripción |
|---|---|
| `users` | Usuarios (id, username, email, hashed_password, created_at) |
| `recipes` | Recetas con todos sus campos, JSONB para ingredientes/pasos/tags, FK a users |
| `inventory_items` | Ingredientes del inventario por usuario, FK a users |

Las relaciones tienen `cascade="all, delete-orphan"`: borrar un usuario elimina todas sus recetas e inventario.

### `models.py`
Esquemas Pydantic v2 para validación de entrada y salida:

- `RecipeBase` / `RecipeCreate` / `RecipeUpdate` — valida todos los campos de receta incluyendo rangos (`servings` 1-100, `rating` 0-5, `prep_time`/`cook_time` 0-1440 minutos) y el enum de dificultad (`Fácil`, `Media`, `Difícil`).
- `Recipe` — añade `id` e `is_public` para la respuesta.
- `UserRegister` / `UserLogin` — validación de email (EmailStr), longitud de contraseña (mín. 8 caracteres).

### `auth.py`
Autenticación basada en JWT:

- **Hash de contraseñas:** bcrypt vía `passlib`. `hash_password()` y `verify_password()`.
- **Tokens JWT:** HS256, expiración de 7 días. El secreto se lee de la variable de entorno `JWT_SECRET`; si no está configurada, la app lanza una excepción en el arranque.
- **Dependencia FastAPI:** `get_current_user_id()` se usa como `Depends()` en todos los endpoints protegidos. Extrae el `user_id` del token y lo pasa al handler; si el token es inválido o ha expirado devuelve 401.

### `storage.py`
Gestión segura de imágenes:

1. **Límite de tamaño:** rechaza archivos mayores de 5 MB.
2. **Verificación de magic bytes:** comprueba los bytes reales del archivo (no el Content-Type del cliente) para confirmar que es JPEG, PNG o WebP.
3. **Re-codificación con Pillow:** convierte la imagen a RGB y la guarda como JPEG, eliminando todos los metadatos, canales EXIF y cualquier payload embebido. Limita los megapíxeles a 20M para evitar ataques de descompresión (*decompression bomb*).
4. **Subida a Azure Blob Storage:** usa `DefaultAzureCredential` (Managed Identity en producción) para autenticarse sin credenciales en el código.

---

## Endpoints de la API

### Autenticación
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register` | Registro de usuario (rate limit: 5/min) |
| POST | `/api/auth/login` | Login, devuelve JWT (rate limit: 10/min) |
| GET | `/api/auth/me` | Datos del usuario autenticado |

### Recetas
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/recipes` | Lista recetas del usuario (soporta `?q=` para buscar) |
| POST | `/api/recipes` | Crea una receta |
| GET | `/api/recipes/{id}` | Obtiene una receta por ID |
| PUT | `/api/recipes/{id}` | Actualiza una receta |
| DELETE | `/api/recipes/{id}` | Elimina una receta |
| POST | `/api/recipes/{id}/image` | Sube una imagen para la receta |
| POST | `/api/recipes/{id}/favorite` | Toggle favorito |
| POST | `/api/recipes/{id}/plan` | Toggle "quiero cocinarla" |
| POST | `/api/recipes/{id}/public` | Toggle visibilidad pública/privada |
| POST | `/api/recipes/{id}/cook` | Cocina la receta (descuenta inventario) |
| GET | `/api/shared/{id}` | Receta pública sin autenticación (rate limit: 30/min) |

### Inventario
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/inventory` | Lista todos los ingredientes del usuario |
| POST | `/api/inventory` | Añade un ingrediente |
| PUT | `/api/inventory/{id}` | Actualiza un ingrediente |
| DELETE | `/api/inventory/{id}` | Elimina un ingrediente |
| GET | `/api/inventory/low-stock` | Ingredientes por debajo del umbral mínimo |
| GET | `/api/shopping-list` | Lista de la compra (stock bajo + ingredientes para recetas planificadas) |

Todos los endpoints excepto `/api/auth/register`, `/api/auth/login` y `/api/shared/{id}` requieren el header `Authorization: Bearer <token>`.

---

## Variables de entorno

| Variable | Descripción | Obligatoria |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión PostgreSQL o SQLite | Sí |
| `JWT_SECRET` | Clave para firmar tokens JWT (mín. 32 caracteres) | Sí |
| `BLOB_ACCOUNT_URL` | URL de la cuenta de Azure Blob Storage | Sí |
| `BLOB_CONTAINER` | Nombre del contenedor de imágenes | Sí |
| `AZURE_CLIENT_ID` | Client ID de la Managed Identity (solo en Azure) | En Azure |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Conexión a Azure Application Insights | Opcional |
| `RATELIMIT_ENABLED` | Poner a `false` para desactivar rate limiting en tests | Opcional |

---

## Arrancar en local

```bash
cd app
pip install -r requirements.txt

# Crear .env con las variables necesarias (ver tabla anterior)
# DATABASE_URL puede ser sqlite:///./recipevault.db para desarrollo local

uvicorn app:app --reload --port 8000
```

La app estará en `http://localhost:8000`.

---

## Tests

Los tests usan **SQLite en memoria** y no necesitan ninguna infraestructura externa.

```bash
cd app
pip install -r requirements-test.txt
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Módulos de test

| Archivo | Tipo | Qué cubre |
|---|---|---|
| `test_auth.py` | Unitario + integración | Hash de contraseñas, registro, login |
| `test_auth_required.py` | Integración | 403 sin token, 401 con token inválido en todos los endpoints |
| `test_recipes.py` | Integración | CRUD completo de recetas, casos 404 |
| `test_inventory.py` | Integración | CRUD de inventario, lista de la compra |
| `test_cook.py` | Integración | Descontar stock, operación atómica, conversión de unidades |
| `test_features.py` | Características | Favoritos, planificación, visibilidad pública, low-stock |
| `test_security.py` | Seguridad | Aislamiento entre usuarios |
| `test_validation.py` | Validación | Límites de campos, tipos inválidos, duplicados |
| `test_image_validation.py` | Unitario | Magic bytes, tamaño, re-codificación JPEG |

Los fixtures compartidos están en `tests/conftest.py`: `client`, `new_user`, `auth_headers`, `recipe`, `inventory_item`.