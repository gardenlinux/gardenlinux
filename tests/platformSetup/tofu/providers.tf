terraform {
  required_version = "~> 1.8.0"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.235.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.84.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 6.4.0"
    }
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "3.0.0"
    }
  }
}
