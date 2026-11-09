terraform {
  required_providers {
    stackit = {
      source  = "stackitcloud/stackit"
      version = "~> 0.123.0"
    }
  }
}

provider "stackit" {
  region = var.provider_vars.region
}
