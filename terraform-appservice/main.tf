locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }

  default_app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
    ENABLE_ORYX_BUILD              = "true"
    WEBSITES_PORT                  = "8000"
    PYTHONUNBUFFERED               = "1"
  }
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku

  tags = local.common_tags
}

resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  https_only = true

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

# ── Managed Identity para GitHub Actions (OIDC) ──────────────────────────────

resource "azurerm_user_assigned_identity" "github_mi" {
  name                = var.github_mi_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  tags = local.common_tags
}

# Credencial federada para pushes a main (infra apply + deploys)
resource "azurerm_federated_identity_credential" "github_main" {
  name                = "github-main-branch"
  resource_group_name = azurerm_resource_group.main.name
  parent_id           = azurerm_user_assigned_identity.github_mi.id
  audience            = ["api://AzureADApplications"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"
}

# Credencial federada para Pull Requests (terraform plan)
resource "azurerm_federated_identity_credential" "github_pr" {
  name                = "github-pull-request"
  resource_group_name = azurerm_resource_group.main.name
  parent_id           = azurerm_user_assigned_identity.github_mi.id
  audience            = ["api://AzureADApplications"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:${var.github_org}/${var.github_repo}:pull_request"
}

# Contributor sobre el Resource Group (gestionar App Service)
resource "azurerm_role_assignment" "github_mi_contributor" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.github_mi.principal_id
}

# Storage Blob Data Contributor sobre la cuenta de estado de Terraform
data "azurerm_storage_account" "tfstate" {
  name                = var.tfstate_storage_account_name
  resource_group_name = var.tfstate_resource_group_name
}

resource "azurerm_role_assignment" "github_mi_tfstate" {
  scope                = data.azurerm_storage_account.tfstate.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.github_mi.principal_id
}
