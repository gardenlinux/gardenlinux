terraform {
  required_version = "~> 1.11.8"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 2.0.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.68.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.35.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 8.7.0"
    }
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "3.2.0"
    }
  }
}
