# general
variable "platform" {
  description = "The platform we run on"
  default     = "aws"
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

# AWS
variable "image_file" {
  description = "Source file for the uploaded image"
}

variable "ssh_user" {
  description = "ssh user to connect to instance"
}

variable "region" {
  description = "AWS region"
}

variable "instance_type" {
  description = "AWS machine_type for the instance"
}
