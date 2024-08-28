variable "platform" {
  description = "The platform we run on"
  default     = "aws"
}

variable "region" {
  description = "AWS region"
  default     = "eu-central-1"
}

variable "test_name" {
  description = "Resources will include this string for reference"
}

variable "image_source" {
  description = "Source file for the uploaded image"
}

variable "instance_type" {
  description = "AWS machine_type for the instance"
  default     = "t3.micro"
}

variable "ssh_public_key" {
  description = "ssh public key to connect to instance"
  default     = "~/.ssh/id_ed25519.pub"
}

variable "ssh_user" {
  description = "ssh user to connect to instance"
  default     = "admin"
}
