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

variable "resource_group_name" {
  description = "Nombre del Resource Group ya existente."
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
  default     = "F1"
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
  default     = "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 backend.main:app"
}

variable "app_settings" {
  description = "Variables de entorno extra para la aplicacion."
  type        = map(string)
  default     = {}
}
