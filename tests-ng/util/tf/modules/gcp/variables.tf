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

variable "existing_root_disk" {
  description = "Optional: Existing AMI to launch instead of importing root disk"
  type        = string
  default     = ""
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

variable "instance_type_amd64" {
  description = "Default instance type for amd64"
  type        = string
  default     = "n1-standard-2"
}

variable "instance_type_arm64" {
  description = "Default instance type for arm64"
  type        = string
  default     = "t2a-standard-2"
}

variable "image_requirements" {
  description = "Runtime requirements to boot the image"
  type = object({
    arch        = string
    uefi        = optional(bool, false)
    secureboot = optional(bool, false)
    tpm2        = optional(bool, false)
  })

  validation {
    condition     = contains(["amd64", "arm64"], var.image_requirements.arch)
    error_message = "arch must be amd64 or arm64"
  }
}

variable "my_ip" {
  description = "Public IPv4 address of machine we're running on"
  type        = string
}

variable "provider_vars" {
  description = "GCP specific settings"

  type = object({
    region             = optional(string, "europe-west4")
    region_storage     = optional(string, "europe-west4")
    instance_type      = optional(string)
    boot_mode          = optional(string)
    net_cidr           = optional(string, "10.0.0.0/16")
    subnet_cidr = optional(string, "10.0.1.0/24")
    ssh_user = optional(string, "gardenlinux")
    gcp_project_id         = string
    zone = optional(string, "a")
    # feature_tpm2      = optional(bool, false)
    # feature_trustedboot = optional(bool, false)
  })
}
