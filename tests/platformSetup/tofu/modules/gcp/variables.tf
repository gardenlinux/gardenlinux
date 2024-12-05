# general
variable "platform" {
  description = "The platform we run on"
  default     = "gcp"
}

variable "arch" {
  description = "Machine architecture to deploy"
}

variable "features" {
  description = "Features to build (based on flavor)."
}

variable "test_name" {
  description = "Resources will include this string for reference"
}

variable "image_path" {
  description = "Source path for the uploaded image"
}

variable "net_range" {
  description = "Subnet range for instance subnet. Not used."
}

variable "subnet_range" {
  description = "Subnet range for instance subnet"
}

variable "ssh_public_key" {
  description = "ssh public key to connect to instance"
}

variable "my_ip" {
  description = "IP address of developer machine for firewall exceptions"
}

# GCP
variable "image_file" {
  description = "Source file for the uploaded image"
}

variable "ssh_user" {
  description = "ssh user to connect to instance"
  default     = "gardenlinux"
}

variable "project_id" {
  description = "GCP project ID"
}

variable "region" {
  description = "GCP region"
}

variable "region_storage" {
  description = "GCP storage region"
}

variable "zone" {
  description = "GCP zone within a region"
}

variable "instance_type" {
  description = "GCP machine_type for the instance"
}
