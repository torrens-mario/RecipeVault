data "azurerm_client_config" "current" {}

# ── Passwords & secrets ────────────────────────────────────────────────────────

resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

# ── Locals ─────────────────────────────────────────────────────────────────────

locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }

  db_url = "postgresql://${var.db_admin_username}:${random_password.db_password.result}@${azurerm_postgresql_flexible_server.main.fqdn}/${var.db_name}?sslmode=require"

  default_app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
    ENABLE_ORYX_BUILD              = "true"
    WEBSITES_PORT                  = "8000"
    PYTHONUNBUFFERED               = "1"
    AZURE_CLIENT_ID                = azurerm_user_assigned_identity.app.client_id
    DATABASE_URL                   = local.db_url
    JWT_SECRET                     = random_password.jwt_secret.result
    BLOB_ACCOUNT_URL                        = "https://${azurerm_storage_account.main.name}.blob.core.windows.net"
    BLOB_CONTAINER                          = azurerm_storage_container.images.name
    APPLICATIONINSIGHTS_CONNECTION_STRING   = azurerm_application_insights.main.connection_string
  }
}

# ── Resource Group ─────────────────────────────────────────────────────────────

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# ── User Assigned Managed Identity (para App Service) ─────────────────────────

resource "azurerm_user_assigned_identity" "app" {
  name                = "${var.app_service_name}-id"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = local.common_tags
}

# ── Storage Account (imagenes de recetas) ──────────────────────────────────────

resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = local.common_tags
}

resource "azurerm_storage_container" "images" {
  name                  = "recipe-images"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "blob"
}

# ── PostgreSQL Flexible Server ─────────────────────────────────────────────────

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = var.db_server_name
  resource_group_name    = azurerm_resource_group.main.name
  location               = var.db_location
  version                = "16"
  administrator_login    = var.db_admin_username
  administrator_password = random_password.db_password.result
  storage_mb             = 32768
  sku_name               = var.db_sku
  tags                   = local.common_tags

  lifecycle {
    ignore_changes = [zone]
  }
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# ── Key Vault ──────────────────────────────────────────────────────────────────

resource "azurerm_key_vault" "main" {
  name                      = var.key_vault_name
  location                  = azurerm_resource_group.main.location
  resource_group_name       = azurerm_resource_group.main.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  tags                      = local.common_tags
}

resource "azurerm_role_assignment" "deployer_kv_secrets_officer" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "time_sleep" "wait_for_kv_rbac" {
  depends_on      = [azurerm_role_assignment.deployer_kv_secrets_officer]
  create_duration = "120s"
}

resource "azurerm_key_vault_secret" "db_url" {
  name         = "DATABASE-URL"
  value        = local.db_url
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [time_sleep.wait_for_kv_rbac]
}

resource "azurerm_key_vault_secret" "jwt_secret" {
  name         = "JWT-SECRET"
  value        = random_password.jwt_secret.result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [time_sleep.wait_for_kv_rbac]
}

# ── Log Analytics Workspace ────────────────────────────────────────────────────

resource "azurerm_log_analytics_workspace" "main" {
  name                = "recipevault-law-dev"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

# ── Application Insights ───────────────────────────────────────────────────────

resource "azurerm_application_insights" "main" {
  name                = "recipevault-ai-dev"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.common_tags
}

# ── App Service Plan ───────────────────────────────────────────────────────────

resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku
  tags                = local.common_tags
}

# ── App Service ────────────────────────────────────────────────────────────────

resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.app.id]
  }

  site_config {
    always_on           = var.app_service_plan_sku != "F1"
    minimum_tls_version = "1.2"
    app_command_line    = var.startup_command

    application_stack {
      python_version = var.python_version
    }
  }

  app_settings = merge(var.app_settings, local.default_app_settings)

  tags = local.common_tags
}

# ── Role assignments para la UAI del App Service ───────────────────────────────

resource "azurerm_role_assignment" "app_kv_secrets_user" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.app.principal_id
}

resource "azurerm_role_assignment" "app_storage_blob_contributor" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.app.principal_id
}
