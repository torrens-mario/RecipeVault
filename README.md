# RecipeVault

Aplicación web de gestión de recetas de cocina desarrollada como proyecto de la asignatura de **Seguridad en la Nube**. Permite guardar recetas personales, gestionar el inventario de ingredientes, generar listas de la compra automáticas y compartir recetas públicamente.

---

## Tabla de contenidos

- [Funcionalidades](#funcionalidades)
- [Arquitectura](#arquitectura)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Stack tecnológico](#stack-tecnológico)
- [Variables de entorno](#variables-de-entorno)
- [Ejecución en local](#ejecución-en-local)
- [Tests](#tests)
- [Seguridad del código fuente](#seguridad-del-código-fuente)
- [Despliegue desde cero](#despliegue-desde-cero)
- [Seguridad](#seguridad)
- [Logs y monitorización](#logs-y-monitorización)
- [Bugs encontrados y solucionados](#bugs-encontrados-y-solucionados)
- [Resolución de problemas](#resolución-de-problemas)

---

## Funcionalidades

### Recetas
- Crear, editar y eliminar recetas con título, descripción, categoría, ingredientes, pasos, etiquetas, dificultad, tiempo de preparación/cocción y notas personales
- Valoración con estrellas (1–5)
- Imagen automática asignada según el tipo de receta (con posibilidad de subir imagen propia en JPEG, PNG o WebP)
- Marcar recetas como **favoritas** o **planificadas para cocinar**
- Filtrar por categoría, dificultad, favoritas o planificadas; ordenar por nombre, valoración o número de ingredientes
- Hacer una receta **pública** (accesible sin login mediante enlace compartido) o **privada**

### Inventario
- Gestionar el stock de ingredientes con nombre, cantidad, unidad y umbral de stock mínimo
- Indicador visual de ingredientes por debajo del umbral, calculado en el servidor (no en el navegador)
- Búsqueda de ingredientes en tiempo real (filtrado local)
- Al "cocinar" una receta, descuenta automáticamente los ingredientes del inventario con conversión de unidades (g↔kg, ml↔l, etc.)

### Lista de la compra
- Generada automáticamente a partir de las recetas planificadas y el inventario actual
- Muestra qué ingredientes faltan y cuáles están por debajo del umbral mínimo

### Usuarios
- Registro e inicio de sesión con email y contraseña
- Recetas e ingredientes de ejemplo precargados al registrarse
- Aislamiento total: cada usuario solo ve y gestiona sus propios datos

---

## Arquitectura

El diagrama interactivo está en [docs/architecture.drawio](docs/architecture.drawio) — ábrelo en [diagrams.net](https://app.diagrams.net).

```
┌─ GitHub Actions ────────────────────────────────────────────────────┐
│  Tests · Build · Deploy  ──── OIDC (sin contraseñas) ─────────────► │
└─────────────────────────────────────────────────────────────────────┘
                                                                       │
┌─ Microsoft Azure ──────────────────────────────────────────────────┐ │
│                                                                    │ │
│  Usuario ──HTTPS──► App Service (FastAPI / Python 3.11) ◄──────────┘ │
│  (navegador)                │                                      │
│                     ┌───────┼───────────────────────┐              │
│                     │       │                        │              │
│                     ▼       ▼                        ▼              │
│             PostgreSQL   Blob Storage        Application Insights   │
│             v16 · SSL    Imágenes            + Log Analytics        │
│                                                                    │
│                   Managed Identity ──RBAC──► Key Vault             │
│                   (sin credenciales)         JWT Secret            │
└────────────────────────────────────────────────────────────────────┘

Terraform ──── terraform apply (IaC) ──────────────────────► Azure
```

El despliegue de la infraestructura está completamente automatizado con **Terraform** y el CI/CD usa **GitHub Actions** con autenticación sin contraseñas mediante **OIDC + Managed Identity**.

---

## Estructura del repositorio

```
RecipeVault/
├── app/
│   ├── app.py              # Endpoints FastAPI (API REST + páginas HTML)
│   ├── database.py         # Acceso a datos (SQLAlchemy, lógica de negocio)
│   ├── db_models.py        # Modelos ORM (tablas de la base de datos)
│   ├── models.py           # Esquemas Pydantic (validación de entrada/salida)
│   ├── auth.py             # JWT: creación y validación de tokens
│   ├── storage.py          # Validación y subida de imágenes a Azure Blob Storage
│   ├── requirements.txt
│   ├── requirements-test.txt
│   ├── frontend/
│   │   ├── templates/      # Páginas HTML (Jinja2)
│   │   └── static/
│   │       ├── css/
│   │       └── js/
│   │           ├── api.js          # Cliente HTTP (fetch wrapper con auth)
│   │           ├── app.js          # Listado y filtrado de recetas
│   │           ├── detail.js       # Detalle de receta
│   │           ├── form.js         # Formulario crear/editar receta
│   │           ├── inventory.js    # Gestión del inventario
│   │           ├── shopping-list.js
│   │           ├── cook.js         # Botón "Cocinar" en detalle de receta
│   │           ├── shared-recipe.js# Vista pública (sin login)
│   │           ├── auth.js         # Login/logout y protección de rutas
│   │           ├── utils.js        # esc(), showToast(), iconForIngredient()
│   │           └── nav-badge.js    # Badge numérico en el icono de compra
│   └── tests/
│       ├── conftest.py             # Fixtures: client, new_user, auth_headers, recipe, inventory_item
│       ├── test_auth.py            # Registro, login, hash de contraseñas
│       ├── test_auth_required.py   # Endpoints protegidos (403 sin token, 401 token inválido)
│       ├── test_recipes.py         # CRUD de recetas + casos 404
│       ├── test_inventory.py       # CRUD de inventario, lista de la compra, casos 404
│       ├── test_cook.py            # Lógica de cocinar: descontar stock, conversión de unidades
│       ├── test_features.py        # Favoritos, visibilidad pública, planificación, low-stock
│       ├── test_security.py        # Aislamiento entre usuarios (recetas e inventario)
│       ├── test_validation.py      # Validación de entrada (límites, tipos, duplicados)
│       └── test_image_validation.py# Validación de imágenes (magic bytes, tamaño, re-codificación)
├── terraform-appservice/           # Infraestructura principal en Azure
├── terraform-state-bootstrap/      # Storage Account para el estado remoto de Terraform
└── .github/workflows/
    ├── tests.yml                   # Tests en cada push a main/mario-dev y en PRs
    ├── deploy-backend.yml          # Despliega backend en cada push a main
    ├── deploy-frontend.yml         # Despliega frontend en cada push a main
    └── infrastructure.yml          # Aplica cambios de infraestructura (manual)
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy · Pydantic v2 |
| Base de datos | PostgreSQL 16 (producción) · SQLite (tests) |
| Autenticación | PyJWT (HS256) · bcrypt (passlib) |
| Rate limiting | slowapi |
| Almacenamiento de imágenes | Azure Blob Storage · Pillow (re-codificación JPEG) |
| Frontend | HTML/CSS/JS vanilla · Jinja2 |
| Infraestructura | Azure App Service · Terraform |
| CI/CD | GitHub Actions · OIDC · Managed Identity |
| Monitorización | Azure Application Insights · Log Analytics |

---

## Variables de entorno

| Variable | Descripción | Obligatoria |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión PostgreSQL (`postgresql://user:pass@host/db?sslmode=require`) | Sí |
| `JWT_SECRET` | Clave secreta para firmar tokens JWT (mín. 32 caracteres) | Sí |
| `BLOB_ACCOUNT_URL` | URL de la cuenta de Storage (`https://<cuenta>.blob.core.windows.net`) | Sí |
| `BLOB_CONTAINER` | Nombre del contenedor de imágenes | Sí |
| `AZURE_CLIENT_ID` | Client ID de la Managed Identity asignada al App Service | En Azure |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Cadena de conexión de Application Insights | Opcional |

En producción, Terraform genera y configura automáticamente todos estos valores. No se almacena ningún secreto en el repositorio.

---

## Ejecución en local

### Requisitos previos
- Python 3.11+
- PostgreSQL (o usar SQLite solo para tests, sin configurar nada)

### Instalación

```bash
cd app
pip install -r requirements.txt
```

### Configurar variables de entorno

Crear un archivo `.env` en `app/` (no se sube al repositorio):

```
DATABASE_URL=postgresql://usuario:contraseña@localhost/recipevault
JWT_SECRET=clave-secreta-larga-minimo-32-caracteres
BLOB_ACCOUNT_URL=https://<cuenta>.blob.core.windows.net
BLOB_CONTAINER=recipe-images
```

### Arrancar el servidor

```bash
cd app
uvicorn app:app --reload --port 8000
```

La aplicación estará disponible en `http://localhost:8000`.

---

## Tests

Los tests usan **SQLite** y no necesitan ninguna infraestructura externa.

```bash
cd app
pip install -r requirements-test.txt
pytest tests/ -v
```

Con reporte de cobertura:

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

**63 tests** organizados en 9 módulos:

| Módulo | Qué cubre |
|---|---|
| `test_auth.py` | Hash de contraseñas, registro, login correcto e incorrecto |
| `test_auth_required.py` | 403 sin token, 401 con token inválido en todos los endpoints protegidos |
| `test_recipes.py` | CRUD completo de recetas, casos 404 para ID inexistente, preservación de favorito al editar |
| `test_inventory.py` | CRUD de inventario, lista de la compra, casos 404 para ID inexistente |
| `test_cook.py` | Descontar stock, operación atómica (fallo parcial no descuenta nada), conversión de unidades, receta inexistente |
| `test_features.py` | Toggle favorito/plan (idempotencia), visibilidad pública/privada, badge de stock bajo |
| `test_security.py` | Aislamiento completo: usuario B no puede leer, modificar ni eliminar datos del usuario A |
| `test_validation.py` | Registro duplicado, cantidades negativas/inválidas, campos fuera de rango (servings, rating, prep_time), longitudes máximas |
| `test_image_validation.py` | Magic bytes, tamaño máximo (5 MB), JPEG/PNG/WebP válidos re-codificados a JPEG, archivos corruptos |

El workflow de GitHub Actions ejecuta los tests automáticamente en cada push a `main` o `mario-dev` y en cada PR hacia `main`.

### Hook pre-commit

El repositorio incluye un hook que ejecuta los tests automáticamente antes de cada `git commit`. Si algún test falla, el commit se cancela.

Para activarlo (solo una vez por máquina, después de clonar el repo):

```bash
cd app
pip install -r requirements-test.txt
cd ..
pre-commit install
```

A partir de ahí el hook se ejecuta solo en cada `git commit`. Para saltarlo puntualmente (no recomendado):

```bash
git commit --no-verify -m "mensaje"
```

---

## Seguridad del código fuente

### Secret scan

El workflow `.github/workflows/secret-scan.yml` ejecuta **Gitleaks** en cada push y PR para detectar secretos (tokens, contraseñas, claves API) accidentalmente incluidos en el código. Si detecta alguno, el workflow falla y bloquea el merge.

El escaneo analiza todo el historial de commits (`fetch-depth: 0`), no solo el último push.

---

## Despliegue desde cero

Pasos completos para desplegar el proyecto en una cuenta de Azure nueva.

### Requisitos previos

- [Azure CLI](https://learn.microsoft.com/es-es/cli/azure/install-azure-cli) instalado
- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.3.0 instalado
- Cuenta de Azure con permisos de Owner o Contributor en la suscripción
- Cuenta de GitHub con acceso al repositorio

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/RecipeVault.git
cd RecipeVault
```

### 2. Iniciar sesión en Azure

```bash
az login
az account show   # Anota el id (subscription ID) y el tenantId
```

### 3. Adaptar los valores del proyecto

Editar `terraform-appservice/provider.tf` y sustituir `tenant_id` y `client_id` con los valores de tu cuenta. También puedes cambiar los nombres de los recursos en `terraform-appservice/variables.tf` (el nombre del App Service y del Storage Account deben ser globalmente únicos en Azure).

### 4. Bootstrap del estado de Terraform

Solo se ejecuta una vez. Crea el Storage Account donde Terraform guardará su estado:

```bash
cd terraform-state-bootstrap
terraform init
terraform apply
```

Si el nombre `tfstaterecipevault` ya está en uso, cámbialo en `terraform-state-bootstrap/terraform.tfvars.example` antes de aplicar.

### 5. Infraestructura principal

```bash
cd ../terraform-appservice
terraform init
terraform apply
```

Terraform crea y configura automáticamente:
- Resource Group con tags de proyecto
- App Service Plan + Linux Web App (Python 3.11)
- PostgreSQL Flexible Server 16 con contraseña generada aleatoriamente
- Storage Account + contenedor de imágenes
- Application Insights + Log Analytics Workspace
- Key Vault con RBAC
- Managed Identity con roles asignados (Storage Blob Data Contributor, Key Vault Secrets User)
- JWT secret generado aleatoriamente

### 6. Configurar los secretos de GitHub para CI/CD

El deploy automático usa OIDC para autenticarse en Azure sin contraseñas. En GitHub → Settings → Secrets and variables → Actions, añade:

| Secret | Cómo obtenerlo |
|---|---|
| `AZURE_CLIENT_ID` | `az identity show --name recipevault-api-dev-id --resource-group recipevault-dev-rg --query clientId -o tsv` |
| `AZURE_TENANT_ID` | `az account show --query tenantId -o tsv` |
| `AZURE_SUBSCRIPTION_ID` | `az account show --query id -o tsv` |

### 7. Primer despliegue

Con los secretos configurados, haz un push a `main`:

```bash
git push origin main
```

GitHub Actions ejecutará los tests y, si pasan, desplegará automáticamente al App Service. Puedes seguir el progreso en la pestaña **Actions** del repositorio.

---

## Seguridad

### Autenticación
- Contraseñas hasheadas con **bcrypt**
- Sesiones mediante **JWT** (HS256), firmados con secreto generado aleatoriamente por Terraform; expiración de 1 semana
- Token enviado en cabecera `Authorization: Bearer <token>`

### Rate limiting
- Registro: **5 peticiones/minuto** por IP
- Login: **10 peticiones/minuto** por IP
- Recetas compartidas (endpoint público): **30 peticiones/minuto** por IP

### Validación de imágenes
- Verificación de **magic bytes** reales del archivo (no se confía en el Content-Type del cliente)
- Re-codificación con Pillow a JPEG: elimina metadatos, payloads embebidos y canales EXIF potencialmente maliciosos
- Límite de **5 MB** y límite de megapíxeles para evitar ataques de descompresión (*decompression bomb*)
- Formatos aceptados: JPEG, PNG y WebP

### Infraestructura
- **Managed Identity** (OIDC): el App Service accede a Storage y Key Vault sin credenciales; GitHub Actions se autentica en Azure sin contraseñas almacenadas
- **HTTPS obligatorio**: `https_only = true` en el App Service, TLS 1.2 mínimo
- **Aislamiento de red**: PostgreSQL solo acepta conexiones desde servicios Azure
- **RBAC en Key Vault**: acceso con permisos mínimos (`Key Vault Secrets User`)

### Políticas de Azure
- **Política HTTPS en Blob Storage**: bloquea tráfico HTTP sin cifrar hacia el Storage Account
- **Política de tags obligatorios**: todos los recursos deben tener tags `Project`, `Environment`, `Owner`, `CostCenter` y `ManagedBy`

### Código
- Todos los endpoints autenticados verifican que el recurso pertenece al `user_id` extraído del JWT, no del cliente
- Los campos `favorite`, `image` y `planned_to_cook` solo se modifican por sus endpoints dedicados; la edición de receta nunca los toca
- Prevención de XSS: toda salida de datos de usuario en el frontend pasa por la función `esc()`
- Índices de base de datos en `user_id` de recetas e inventario para evitar escaneos completos de tabla

---

## Logs y monitorización

La aplicación genera tres niveles de log enviados a Application Insights:

| Nivel | Cuándo |
|---|---|
| `INFO` | Operaciones normales: registro, login, creación/eliminación de recetas, ingredientes añadidos |
| `WARNING` | Accesos fallidos, credenciales incorrectas, recursos no encontrados |
| `ERROR` | Fallos críticos: errores de base de datos, excepciones no controladas |

Para consultar los logs en Application Insights (Azure Portal → Application Insights → Logs):

```kusto
traces
| where timestamp > ago(1h)
| order by timestamp desc
```

---

## Bugs encontrados y solucionados

Durante el desarrollo y las rondas de auditoría se detectaron y corrigieron los siguientes problemas:

### Editar una receta reseteaba el favorito y el estado "quiero cocinarla"
**Problema:** el formulario de edición enviaba siempre `favorite: false` y `planned_to_cook: false` en el payload. La función `update_recipe` los aplicaba, borrando cualquier marcado previo del usuario.  
**Solución:** `update_recipe` ignora explícitamente `image`, `favorite` y `planned_to_cook`; solo los endpoints dedicados (`/favorite`, `/plan`, `/image`) pueden cambiarlos.

### El endpoint `/cook` devolvía 400 en vez de 404 para recetas inexistentes
**Problema:** `consume_ingredients_for_recipe` devolvía `{"success": false, "error": "..."}` cuando la receta no existía, y el endpoint respondía con un 400 genérico.  
**Solución:** el endpoint comprueba la existencia de la receta antes de llamar a la función de consumo y devuelve 404 si no existe.

### Valores de dificultad no estándar en base de datos crasheaban la app
**Problema:** si un registro en la BD tenía un valor de `difficulty` distinto de "Fácil", "Media" o "Difícil" (ej. datos migrados), Pydantic lanzaba una excepción al construir el modelo y devolvía un 500.  
**Solución:** `_recipe_row_to_model` sanitiza el valor antes de pasarlo a Pydantic; los inválidos se normalizan a "Media". Además se añadió un `field_validator` en el modelo para rechazar valores fuera del conjunto válido en la entrada.

### El cálculo de stock bajo dependía del cliente, no del servidor
**Problema:** `inventory.js` calculaba localmente si un ingrediente estaba en stock bajo comparando cantidades numéricas, sin tener en cuenta la unidad del umbral. Esto producía resultados incorrectos cuando las unidades diferían (ej. threshold en kg, stock en g).  
**Solución:** el frontend ahora consulta el endpoint `/api/inventory/low-stock` (que usa la lógica de conversión de unidades del servidor) y mantiene un `Set` de IDs en stock bajo para renderizar la UI.

### El endpoint público de recetas compartidas no tenía rate limit
**Problema:** `/api/shared/{recipe_id}` era el único endpoint de la API accesible sin autenticación y no tenía ningún límite de peticiones, dejándolo expuesto a scraping masivo.  
**Solución:** añadido `@limiter.limit("30/minute")` al igual que los endpoints de registro y login.

### Fallos de red en el inventario producían un estado vacío silencioso
**Problema:** `loadInventory()` en `inventory.js` no tenía manejo de errores. Si la llamada a la API fallaba (ej. timeout), la tabla se quedaba vacía sin ningún mensaje al usuario.  
**Solución:** añadido `try/catch` que muestra un mensaje de error explícito en la tabla cuando la carga falla.

### Código muerto en `api.js` (`uploadRecipeImage`)
**Problema:** `api.js` definía un método `uploadRecipeImage` que nunca se llamaba; `detail.js` usaba `fetch` directamente para la subida de imágenes.  
**Solución:** método eliminado.

### Búsqueda sin límite de longitud en el frontend y el backend
**Problema:** el campo de búsqueda en `index.html` no tenía `maxlength`, y el parámetro `q` en el backend tampoco se truncaba, permitiendo consultas SQL con cadenas arbitrariamente largas.  
**Solución:** añadido `maxlength="200"` al input HTML y truncado del parámetro en el servidor antes de usarlo en la query.

---

## Resolución de problemas

### La app no arranca / error 500 al abrir

**Causa más común:** las variables de entorno no están configuradas.

Comprueba en Azure Portal → App Service → Environment variables que existen `DATABASE_URL`, `JWT_SECRET`, `BLOB_ACCOUNT_URL` y `BLOB_CONTAINER`. Si falta alguna, vuelve a ejecutar `terraform apply`.

Para ver el error exacto: App Service → **Log stream** (en tiempo real) o App Service → **Diagnose and solve problems**.

---

### El deploy de GitHub Actions falla con error de autenticación

**Causa:** los secretos de GitHub (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`) no están configurados o son incorrectos.

```bash
az account show --query "{tenantId:tenantId, subscriptionId:id}" -o table
az identity show --name recipevault-api-dev-id --resource-group recipevault-dev-rg --query clientId -o tsv
```

---

### `terraform apply` falla con "already exists"

**Causa:** los nombres del Storage Account y del App Service son globalmente únicos en Azure.

```hcl
# terraform-appservice/variables.tf
variable "storage_account_name" {
  default = "recipevaultimgdev"   # ← cámbialo por algo único
}
variable "app_service_name" {
  default = "recipevault-api-dev" # ← cámbialo si ya existe
}
```

---

### No aparecen logs en Application Insights

1. Comprueba que `APPLICATIONINSIGHTS_CONNECTION_STRING` está en las variables del App Service
2. Visita la app y realiza alguna acción (login, crear receta)
3. Espera 2–5 minutos (hay delay de ingesta)
4. Ejecuta la query sin filtro de tiempo:

```kusto
traces
| order by timestamp desc
| take 50
```

---

### Los tests fallan localmente

```bash
cd app
pip install -r requirements-test.txt
pytest tests/ -v
```

Los tests no necesitan base de datos ni Azure — usan SQLite automáticamente.

---

### Error al subir imágenes (Blob Storage)

**Causa:** la Managed Identity no tiene el rol `Storage Blob Data Contributor` en el Storage Account.

Verifica en Azure Portal → Storage Account → Access Control (IAM) → Role assignments que aparece `recipevault-api-dev-id` con ese rol. Si no aparece, ejecuta `terraform apply`.
