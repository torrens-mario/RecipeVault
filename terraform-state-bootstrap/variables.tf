locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}

variable "project" {
  description = "Nombre del proyecto."
  type        = string
  default     = "RecipeVault"
}

variable "environment" {
  description = "Entorno compartido del backend remoto."
  type        = string
  default     = "shared"
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
  description = "Nombre del Resource Group del state remoto."
  type        = string
  default     = "terraform-state-rg"
}

variable "location" {
  description = "Region de Azure para el backend remoto."
  type        = string
  default     = "Germany West Central"
}

variable "storage_account_name" {
  description = "Nombre unico global del Storage Account para el state."
  type        = string
  default     = "tfstaterecipevault"
}

variable "container_name" {
  description = "Contenedor donde se guarda el state remoto."
  type        = string
  default     = "tfstate"
}
