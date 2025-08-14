variable "prefix" {
  description = "Prefix to use for resource names"
  type        = string
  default     = "gardenlinux-test"
}

variable "root_disk_path" {
  description = "Path of the root disk image to use"
  type        = string
}

variable "test_disk_path" {
  description = "Path of the test disk image to use"
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to your ssh public key"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "user_data_script_path" {
  description = "Script to run on VM boot"
  type        = string
}

variable "image_requirements" {
  description = "Runtime requirements to boot the image"
  type = object({
    arch        = string
    uefi        = optional(bool, false)
    secure_boot = optional(bool, false)
    tpm2        = optional(bool, false)
  })

  validation {
    condition     = contains(["x86_64", "arm64"], var.image_requirements.arch)
    error_message = "arch must be x86_64 or arm64"
  }
}

variable "my_ip" {
  description = "Public IPv4 address of machine we're running on"
  type        = string
}

variable "provider_vars" {
  description = "AWS sepcific settings"

  type = object({
    region             = optional(string, "eu-central-1")
    instance_type      = optional(string)
    boot_mode          = optional(string)
    vpc_cidr           = optional(string, "10.0.0.0/16")
    public_subnet_cidr = optional(string, "10.0.1.0/24")
  })
}

variable "use_scp" {
  description = "If true, do not attach test disk; scp dist.tar.gz to instance instead"
  type        = bool
}
