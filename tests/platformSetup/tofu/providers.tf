terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.235.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.65.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 6.4.0"
    }
  }
}
