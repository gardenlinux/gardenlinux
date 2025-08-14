terraform {
  required_version = "~> 1.0"
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.0"
    }
  }
}

locals {
  provider_modules = {
    aws   = "./modules/aws"
    gcp   = "./modules/gcp"
    azure = "./modules/azure"
  }
}

module "cloud" {
  source = local.provider_modules[var.cloud_provider]

  prefix                = "${var.prefix}-${random_id.suffix.hex}"
  root_disk_path        = var.root_disk_path
  test_disk_path        = var.test_disk_path
  ssh_public_key_path   = var.ssh_public_key_path
  user_data_script_path = var.user_data_script_path
  image_requirements    = var.image_requirements
  my_ip                 = chomp(data.http.my_ip.response_body)
  provider_vars         = try(var.provider_vars[var.cloud_provider], {})
  use_scp               = var.use_scp
}

resource "random_id" "suffix" {
  byte_length = 4
}

data "http" "my_ip" {
  url = "https://api.ipify.org"
}

output "vm_ip" {
  value       = module.cloud.vm_ip
  description = "Public IPv4 of the VM"
}
