# RecipeVault

Aplicación web de gestión de recetas de cocina desarrollada como proyecto de la asignatura de **Seguridad en la Nube**. Permite guardar recetas personales, gestionar el inventario de ingredientes, generar listas de la compra automáticas y compartir recetas públicamente.

---

## Funcionalidades

### Recetas
- Crear, editar y eliminar recetas con título, descripción, categoría, ingredientes, pasos, etiquetas, dificultad, tiempo de preparación/cocción y notas
- Valoración con estrellas (1-5)
- Imagen automática asignada según el tipo de receta (con posibilidad de subir imagen propia)
- Marcar recetas como **favoritas** o **planificadas para cocinar**
- Filtrar por categoría, favoritas o planificadas
- Ordenar por fecha, nombre o mejor valoradas
- Hacer una receta **pública** (accesible sin login mediante enlace compartido) o **privada**

### Inventario
- Gestionar el stock de ingredientes con nombre, cantidad, unidad y umbral de stock mínimo
- Indicador visual de ingredientes por debajo del umbral
- Búsqueda de ingredientes en tiempo real
- Al "cocinar" una receta, descuenta automáticamente los ingredientes del inventario

### Lista de la compra
- Generada automáticamente a partir de las recetas planificadas y el inventario actual
- Muestra qué ingredientes faltan y cuáles están por debajo del umbral

### Usuarios
- Registro e inicio de sesión con email y contraseña
- Recetas e ingredientes de ejemplo precargados al registrarse
- Cada usuario solo ve y gestiona sus propios datos

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
│   ├── auth.py             # Creación y validación de tokens JWT
│   ├── storage.py          # Subida de imágenes a Azure Blob Storage
│   ├── requirements.txt
│   ├── requirements-test.txt
│   ├── frontend/
│   │   ├── templates/      # Páginas HTML (Jinja2)
│   │   └── static/         # CSS y JavaScript
│   └── tests/
│       ├── conftest.py         # Fixtures compartidos (cliente, usuario, receta)
│       ├── test_auth.py        # Tests de registro y login
│       ├── test_recipes.py     # Tests CRUD de recetas
│       ├── test_inventory.py   # Tests CRUD de inventario y lista de la compra
│       └── test_features.py    # Tests de favoritos y visibilidad pública
├── terraform-appservice/       # Infraestructura principal en Azure
├── terraform-state-bootstrap/  # Storage Account para el estado remoto de Terraform
└── .github/workflows/          # Pipelines de CI/CD
    ├── tests.yml               # Ejecuta los tests en cada PR y push a main
    ├── deploy-backend.yml      # Despliega el backend en cada push a main
    └── infrastructure.yml      # Aplica cambios de infraestructura (manual)
```

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
- PostgreSQL (o usar SQLite solo para tests)

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

Los tests usan **SQLite en memoria** y no necesitan ninguna infraestructura externa.

```bash
cd app
pip install -r requirements-test.txt
pytest tests/ -v
```

Cobertura actual: **19 tests** — autenticación, recetas (CRUD), inventario (CRUD), features (favoritos, visibilidad pública).

El workflow de GitHub Actions ejecuta los tests automáticamente en cada PR y push a `main`.

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

Si el nombre `tfstaterecipevault` ya está en uso (es globalmente único), cámbialo en `terraform-state-bootstrap/terraform.tfvars.example` antes de aplicar.

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

Al terminar, Terraform muestra los outputs con la URL de la app y los nombres de los recursos.

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
- Sesiones mediante **JWT** (HS256), firmados con secreto generado aleatoriamente por Terraform
- Token enviado en cabecera `Authorization: Bearer <token>`

### Infraestructura
- **Managed Identity** (OIDC): el App Service accede a Storage y Key Vault sin credenciales; GitHub Actions se autentica en Azure sin contraseñas almacenadas
- **HTTPS obligatorio**: `https_only = true` en el App Service, TLS 1.2 mínimo
- **Aislamiento de red**: PostgreSQL solo acepta conexiones desde servicios Azure (`AllowAzureServices`)
- **RBAC en Key Vault**: acceso al vault con permisos mínimos (`Key Vault Secrets User`)

### Políticas de Azure
- **Política HTTPS en Blob Storage**: obliga a que todo el tráfico hacia el Storage Account use HTTPS, bloqueando HTTP sin cifrar
- **Política de tags obligatorios**: todos los recursos deben tener tags `Project`, `Environment`, `Owner`, `CostCenter` y `ManagedBy`, lo que permite auditoría de costos e identificación de responsables

### Código
- Validación de entrada en todos los endpoints con Pydantic
- Aislamiento por usuario: cada consulta filtra por `user_id` extraído del JWT, sin confiar en el cliente
- Recetas públicas/privadas: endpoint dedicado para cambiar visibilidad, independiente de la edición

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

## Resolución de problemas

### La app no arranca / error 500 al abrir

**Causa más común:** las variables de entorno no están configuradas.

Comprueba en Azure Portal → App Service → Environment variables que existen `DATABASE_URL`, `JWT_SECRET`, `BLOB_ACCOUNT_URL` y `BLOB_CONTAINER`. Si falta alguna, significa que Terraform no aplicó correctamente — vuelve a ejecutar `terraform apply`.

Para ver el error exacto: App Service → **Log stream** (en tiempo real) o App Service → **Diagnose and solve problems**.

---

### El deploy de GitHub Actions falla con error de autenticación

**Causa:** los secretos de GitHub (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`) no están configurados o son incorrectos.

Verifica los valores con:
```bash
az account show --query "{tenantId:tenantId, subscriptionId:id}" -o table
az identity show --name recipevault-api-dev-id --resource-group recipevault-dev-rg --query clientId -o tsv
```

---

### `terraform apply` falla con "already exists" o conflicto de nombre

**Causa:** los nombres del Storage Account y del App Service son globalmente únicos en Azure. Si ya existen de un deploy anterior o los usa otra cuenta, cambia los valores por defecto en `terraform-appservice/variables.tf`:

```hcl
variable "storage_account_name" {
  default = "recipevaultimgdev"   # ← cámbialo por algo único
}
variable "app_service_name" {
  default = "recipevault-api-dev" # ← cámbialo si ya existe
}
```

---

### No aparecen logs en Application Insights

1. Comprueba que `APPLICATIONINSIGHTS_CONNECTION_STRING` está en las variables de entorno del App Service
2. Visita la app y realiza alguna acción (login, crear receta)
3. Espera 2-5 minutos (hay delay de ingesta)
4. Ejecuta la query sin filtro de tiempo:
```kusto
traces
| order by timestamp desc
| take 50
```

---

### Los tests fallan localmente

Asegúrate de estar en el directorio correcto y de tener las dependencias de test instaladas:

```bash
cd app
pip install -r requirements-test.txt
pytest tests/ -v
```

Los tests no necesitan base de datos ni Azure — usan SQLite en memoria automáticamente.

---

### Error al subir imágenes (Blob Storage)

**Causa:** la Managed Identity del App Service no tiene el rol `Storage Blob Data Contributor` en el Storage Account.

Verifica en Azure Portal → Storage Account → Access Control (IAM) → Role assignments que aparece la identidad `recipevault-api-dev-id` con ese rol. Si no aparece, vuelve a ejecutar `terraform apply`.
