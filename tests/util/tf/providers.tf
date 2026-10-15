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
    # stil using fork with secureboot certificate support
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.9.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 8.7.0"
    }
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "3.4.0"
    }
  }
}
