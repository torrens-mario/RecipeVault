output "backend_config" {
  description = "Bloque backend azurerm para copiar en otros proyectos Terraform."
  value = <<-EOT
backend "azurerm" {
  resource_group_name  = "${azurerm_resource_group.tfstate.name}"
  storage_account_name = "${azurerm_storage_account.tfstate.name}"
  container_name       = "${azurerm_storage_container.tfstate.name}"
  key                  = "recipevault-appservice-dev.tfstate"
}
EOT
}

output "resource_group_name" {
  value = azurerm_resource_group.tfstate.name
}

output "storage_account_name" {
  value = azurerm_storage_account.tfstate.name
}

output "container_name" {
  value = azurerm_storage_container.tfstate.name
}
