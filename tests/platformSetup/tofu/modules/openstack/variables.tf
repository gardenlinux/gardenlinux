# general
variable "platform" {
  description = "The platform we run on"
  default     = "openstack"
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

# OpenStack
variable "image_file" {
  description = "Source file for the uploaded image"
}

variable "ssh_user" {
  description = "ssh user to connect to instance"
  default     = "gardenlinux"
}

variable "region" {
  description = "OpenStack region"
}

# variable "region_storage" {
#   description = "OpenStack region for storage. Not used."
# }
# 
# variable "zone" {
#   description = "OpenStack zone within a region. Not used."
# }

variable "instance_type" {
  description = "OpenStack machine_type for the instance"
}

variable "floatingip_pool" {
  description = "OpenStack floatingip pool"
}

variable "public_network_name" {
  description = "OpenStack public network name"
}