terraform {
  required_version = ">= 1.3.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.75"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "azurerm" {
    use_oidc             = true
    use_azuread_auth     = true
    tenant_id            = "78f3a279-48c8-4670-9162-a63c451c9fae"
    client_id            = "27e43fdd-83b9-4881-a6ea-4104ca38bd71"
    storage_account_name = "tfstaterecipevault"
    container_name       = "tfstate"
    key                  = "recipevault-appservice-dev.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

provider "random" {}
