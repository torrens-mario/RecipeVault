output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "app_service_plan_name" {
  value = azurerm_service_plan.main.name
}

output "app_service_name" {
  value = azurerm_linux_web_app.main.name
}

output "app_service_default_hostname" {
  value = azurerm_linux_web_app.main.default_hostname
}

output "backend_url" {
  value = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "app_service_principal_id" {
  value = azurerm_linux_web_app.main.identity[0].principal_id
}

output "db_server_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "key_vault_name" {
  value = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}
