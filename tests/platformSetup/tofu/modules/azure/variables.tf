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
  description = "Net range for instance net"
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

# Azure
variable "image_file" {
  description = "Source file for the uploaded image"
}

variable "ssh_user" {
  description = "ssh user to connect to instance"
  default     = "gardenlinux"
}

variable "region" {
  description = "Azure region"
}

# variable "region_store" {
#   description = "Azure region for storage. Not used."
# }
# 
# variable "zone" {
#   description = "Azure zone within a region. Not used."
# }

variable "instance_type" {
  description = "Azure machine_type for the instance"
}
