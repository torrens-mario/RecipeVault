resource "azurerm_resource_group" "tfstate" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

resource "azurerm_storage_account" "tfstate" {
  name                         = var.storage_account_name
  resource_group_name          = azurerm_resource_group.tfstate.name
  location                     = azurerm_resource_group.tfstate.location
  account_tier                 = "Standard"
  account_replication_type     = "LRS"
  https_traffic_only_enabled   = true

  tags = local.common_tags
}

resource "azurerm_storage_container" "tfstate" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}

resource "azurerm_management_lock" "tfstate_rg" {
  name       = "DoNotDelete"
  scope      = azurerm_resource_group.tfstate.id
  lock_level = "CanNotDelete"
  notes      = "Protege el backend de Terraform"
}
