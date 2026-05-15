project     = "RecipeVault"
environment = "dev"
owner       = "mario_torrens@euneiz.com"
cost_center = "personal"

resource_group_name = "recipevault-dev-rg"

app_service_plan_name = "recipevault-asp-dev"
app_service_plan_sku  = "B1"

app_service_name = "recipevault-api-dev"
python_version   = "3.11"
startup_command  = "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app:app --timeout 600"

app_settings = {
  ENVIRONMENT                    = "dev"
  SCM_DO_BUILD_DURING_DEPLOYMENT = "false"
  ENABLE_ORYX_BUILD              = "false"
}