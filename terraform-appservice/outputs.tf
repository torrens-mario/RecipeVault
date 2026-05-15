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

output "managed_identity_client_id" {
  description = "Client ID de la Managed Identity — usar como AZURE_CLIENT_ID en los secretos de GitHub."
  value       = azurerm_user_assigned_identity.github_mi.client_id
}