terraform {
  required_version = "1.10.6"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "1.257.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "6.8.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.35.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "6.48.0"
    }
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "3.3.2"
    }
  }
}
