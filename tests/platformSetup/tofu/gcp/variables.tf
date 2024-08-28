variable "project_id" {
  description = "GCP project ID"
}

variable "platform" {
  description = "The platform we run on"
  default = "gcp"
}

variable "region" {
  description = "GCP region"
  default     = "europe-west3"
}

variable "region_storage" {
  description = "GCP storage region"
  default     = "europe-west3"
}

variable "zone" {
  description = "GCP zone within a region"
  default     = "a"
}

variable "test_name" {
  description = "Resources will include this string for reference"
}

variable "image_source" {
  description = "Source file for the uploaded image"
}

variable "subnet_range" {
  description = "Subnet range for instance subnet"
  default     = "10.242.10.0/24"
}

variable "instance_type" {
  description = "GCP machine_type for the instance"
  default     = "n1-standard-2"
}

variable "ssh_public_key" {
  description = "ssh public key to connect to instance"
  default     = "~/.ssh/id_ed25519.pub"
}

variable "ssh_user" {
  description = "ssh user to connect to instance"
  default     = "gardenlinux"
}
