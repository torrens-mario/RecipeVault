variable "project" {
  description = "Nombre del proyecto."
  type        = string
  default     = "RecipeVault"
}

variable "environment" {
  description = "Entorno de despliegue."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Responsable del proyecto."
  type        = string
  default     = "mario_torrens@euneiz.com"
}

variable "cost_center" {
  description = "Centro de coste."
  type        = string
  default     = "personal"
}

variable "location" {
  description = "Region de Azure."
  type        = string
  default     = "Germany West Central"
}

variable "resource_group_name" {
  description = "Nombre del Resource Group."
  type        = string
  default     = "recipevault-dev-rg"
}

variable "app_service_plan_name" {
  description = "Nombre del App Service Plan."
  type        = string
  default     = "recipevault-asp-dev"
}

variable "app_service_plan_sku" {
  description = "SKU del plan."
  type        = string
  default     = "B1"
}

variable "app_service_name" {
  description = "Nombre globalmente unico de la Web App."
  type        = string
  default     = "recipevault-api-dev"
}

variable "python_version" {
  description = "Version de Python para App Service Linux."
  type        = string
  default     = "3.11"
}

variable "startup_command" {
  description = "Comando de arranque de FastAPI."
  type        = string
  default     = "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app:app --timeout 600"
}

variable "app_settings" {
  description = "Variables de entorno extra para la aplicacion."
  type        = map(string)
  default     = {}
}

# ── Storage ────────────────────────────────────────────────────────────────────

variable "storage_account_name" {
  description = "Nombre de la Storage Account para imagenes (3-24 chars, solo minusculas y numeros)."
  type        = string
  default     = "recipevaultimgdev"
}

# ── PostgreSQL ─────────────────────────────────────────────────────────────────

variable "db_location" {
  description = "Region para el servidor PostgreSQL (puede diferir del resto si hay restricciones)."
  type        = string
  default     = "East US"
}

variable "db_server_name" {
  description = "Nombre globalmente unico del servidor PostgreSQL Flexible."
  type        = string
  default     = "recipevault-db-dev"
}

variable "db_name" {
  description = "Nombre de la base de datos dentro del servidor."
  type        = string
  default     = "recipevault"
}

variable "db_admin_username" {
  description = "Usuario administrador de PostgreSQL."
  type        = string
  default     = "recipevaultadmin"
}

variable "db_sku" {
  description = "SKU del servidor PostgreSQL Flexible."
  type        = string
  default     = "B_Standard_B1ms"
}

# ── Key Vault ──────────────────────────────────────────────────────────────────

variable "key_vault_name" {
  description = "Nombre globalmente unico del Key Vault (3-24 chars)."
  type        = string
  default     = "recipevault-kv-dev"
}

variable "deployer_principal_id" {
  description = "Principal ID del Managed Identity de GitHub Actions (necesita escribir secretos en KV)."
  type        = string
  default     = "067f8ef3-a303-4ec0-b459-a25b56463479"
}
