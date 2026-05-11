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

resource "null_resource" "deploy_app" {
  depends_on = [time_sleep.wait_for_app]

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = <<EOT
      $appDir = Resolve-Path "${path.module}/../app"
      $zipPath = Join-Path $env:TEMP "recipevault-deploy.zip"
      if (Test-Path $zipPath) { Remove-Item $zipPath }
      Push-Location $appDir
      & "D:\7-Zip\7z.exe" a -tzip $zipPath app.py models.py database.py requirements.txt frontend
      Pop-Location
      az webapp deploy `
        --resource-group ${var.resource_group_name} `
        --name ${var.app_service_name} `
        --src-path $zipPath `
        --type zip
    EOT
  }

  provisioner "local-exec" {
    when        = destroy
    interpreter = ["PowerShell", "-Command"]
    command     = "Write-Host 'Infraestructura destruida correctamente'"
  }
}

resource "time_sleep" "wait_for_app" {
  depends_on      = [azurerm_linux_web_app.main]
  create_duration = "30s"
}