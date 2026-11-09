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
  description = "Optional: Existing image ID to launch instead of importing root disk"
  type        = string
  default     = ""
}

variable "ssh_public_key_path" {
  description = "Path to your ssh public key"
  type        = string
}

variable "user_data_script_path" {
  description = "Script to run on VM boot"
  type        = string
}

variable "instance_type_amd64" {
  description = "Default instance type for amd64"
  type        = string
  default     = "t1.2"
}

variable "image_requirements" {
  description = "Runtime requirements to boot the image"
  type = object({
    arch        = string
    uefi        = optional(bool, false)
    secureboot  = optional(bool, false)
    tpm2        = optional(bool, false)
  })

  validation {
    condition     = contains(["amd64"], var.image_requirements.arch)
    error_message = "arch must be amd64"
  }
}

variable "my_ip" {
  description = "Public IPv4 address of machine we're running on"
  type        = string
}

variable "provider_vars" {
  description = "STACKIT specific settings"

  type = object({
    project_id        = string
    region            = optional(string, "EU01")
    availability_zone = optional(string, "EU01-1")
    machine_type      = optional(string)
    ssh_user          = optional(string, "gardenlinux")
    net_cidr          = optional(string, "10.0.0.0/16")
    subnet_cidr       = optional(string, "10.0.1.0/24")
  })
}

variable "skip_tests" {
  description = "Skip deploying test disk and running tests"
  type        = bool
  default     = false
}
