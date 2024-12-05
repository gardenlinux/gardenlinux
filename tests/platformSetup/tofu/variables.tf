# general
variable "test_prefix" {
  description = "Resources will include this prefix string for reference"
  validation {
    condition     = length(var.test_prefix) > 0 && length(var.test_prefix) <= 10 && can(regex("^[-a-zA-Z0-9]+$", var.test_prefix))
    error_message = "The test_prefix must be between 1 and 10 characters and can only include alphanumeric characters and hyphens (-)."
  }
}

variable "test_environment" {
  description = "Resources will include this environment string for reference"
  default     = "dev"
}

variable "image_path" {
  description = "Source path for the uploaded image"
  default     = "file:///gardenlinux/.build"
}

variable "net_range" {
  description = "Net range for instance net"
  default     = "10.242.10.0/23"
}

variable "subnet_range" {
  description = "Subnet range for instance subnet"
  default     = "10.242.10.0/24"
}

variable "ssh_public_key" {
  description = "ssh public key to connect to instance"
  default     = "~/.ssh/id_ed25519.pub"
}

variable "flavors" {
  description = "Flavors to build (combination of platform, features, arch)."
  default     = null
}

# state_aws
variable "deploy_state_aws" {
  description = "Deploy resources needed to manage remote state in AWS"
  default     = false
}

# state_aws_kms
variable "deploy_state_aws_kms" {
  description = "Deploy resources needed to manage remote state in AWS via KMS"
  default     = false
}

# ALI
variable "ali_image_file" {
  description = "Source file for the uploaded image"
  default     = "ali-gardener_prod-amd64-today-local.qcow2"
}

variable "ali_ssh_user" {
  description = "ssh user to connect to instance"
  default     = "admin"
}

variable "ali_region" {
  description = "AWS region"
  default     = "eu-central-1"
}

variable "ali_instance_type" {
  description = "AWS instance_type for the instance"
  default     = "ecs.t6-c1m2.large" # amd64
  # default     = "ecs.g8y.small" # arm64
}

# AWS
variable "aws_image_file" {
  description = "Source file for the uploaded image"
  default     = "aws-gardener_prod-amd64-today-local.raw"
}

variable "aws_ssh_user" {
  description = "ssh user to connect to instance"
  default     = "admin"
}

variable "aws_region" {
  description = "AWS region"
  default     = "eu-central-1"
}

variable "aws_instance_type" {
  description = "AWS instance_type for the instance"
  default     = "t3.micro" # amd64
  # default     = "m6g.medium" # amd64
}

# Azure
variable "azure_subscription_id" {
  description = "Azure subscription ID"
  default     = "0000000-0000-00000-000000"
}

variable "azure_image_file" {
  description = "Source file for the uploaded image"
  default     = "azure-gardener_prod-amd64-today-local.vhd"
}

variable "azure_ssh_user" {
  description = "ssh user to connect to instance"
  default     = "azureuser"
}

variable "azure_region" {
  description = "Azure region"
  default     = "westeurope"
}

variable "azure_instance_type" {
  description = "Azure machine_type for the instance"
  default     = "Standard_D4_v4" # amd64
  # default     = "Standard_D4ps_v5" # arm64
}

# GCP
variable "gcp_image_file" {
  description = "Source file for the uploaded image"
  default     = "gcp-gardener_prod-amd64-today-local.gcpimage.tar.gz"
}

variable "gcp_ssh_user" {
  description = "ssh user to connect to instance"
  default     = "gardenlinux"
}

variable "gcp_project_id" {
  description = "GCP project ID"
}

variable "gcp_region" {
  description = "GCP region"
  default     = "europe-west4"
}

variable "gcp_region_storage" {
  description = "GCP storage region"
  default     = "europe-west4"
}

variable "gcp_zone" {
  description = "GCP zone within a region"
  default     = "a"
}

variable "gcp_instance_type" {
  description = "GCP machine_type for the instance"
  default     = "n1-standard-2" # amd64
  # default     = "t2a-standard-2" # arm64
}
