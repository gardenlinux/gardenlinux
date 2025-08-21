terraform {
  required_version = "~> 1.10.0"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.253.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.2.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.35.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 6.42.0"
    }
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "3.2.0"
    }
  }
}
