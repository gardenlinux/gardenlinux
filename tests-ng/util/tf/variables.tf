variable "prefix" {
  description = "Prefix to use for resource names"
  type        = string
  default     = "gl-tests-ng"
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
  default     = "~/.ssh/id_ed25519_gl.pub"
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
    condition     = contains(["amd64", "arm64"], var.image_requirements.arch)
    error_message = "arch must be amd64 or arm64"
  }
}

variable "cloud_provider" {
  description = "Which cloud provider to target"
  type        = string
  validation {
    condition     = contains(["aws", "gcp", "azure", "ali"], var.cloud_provider)
    error_message = "Must be one of aws, gcp, azure, or ali."
  }
}

variable "provider_vars" {
  description = "Cloud provider specific settings"
  type        = map(any)
  default     = {}
}
