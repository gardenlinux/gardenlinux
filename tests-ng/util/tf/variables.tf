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

variable "cloud_provider" {
  description = "Which cloud provider to target"
  type        = string
  validation {
    condition     = contains(["aws", "gcp", "azure"], var.cloud_provider)
    error_message = "Must be one of aws, gcp, or azure."
  }
}

variable "provider_vars" {
  description = "Cloud provider specific settings"
  type        = map(any)
  default     = {}
}

variable "use_scp" {
  description = "If true, do not attach test disk; scp dist.tar.gz to instance instead"
  type        = bool
  default     = false
}
