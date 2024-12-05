output "public_ips" {
  description = "Public IP addresses for all dynamically created modules"
  value = {
    for config in local.module_config : config.name => try(
      (
        config.platform == "gcp" ? module.gcp[config.name].public_ip :
        config.platform == "azure" ? module.azure[config.name].public_ip :
        config.platform == "aws" ? module.aws[config.name].public_ip :
        config.platform == "ali" ? module.ali[config.name].public_ip :
        null
      ),
      null
    )
  }
}

output "ssh_users" {
  description = "SSH users for all dynamically created modules"
  value = {
    for config in local.module_config : config.name => config.ssh_user
  }
}

output "instance_types" {
  description = "Instance types for all dynamically created modules"
  value = {
    for config in local.module_config : config.name => config.instance_type
  }
}

output "features" {
  description = "Features enabled for all dynamically created modules"
  value = {
    for config in local.module_config : config.name => config.features
  }
}

output "architectures" {
  description = "Architectures of all dynamically created modules"
  value = {
    for config in local.module_config : config.name => config.arch
  }
}

# Outputs for general module configurations
output "module_config" {
  description = "Complete module configuration details for dynamically created modules"
  value       = local.module_config
}

# Outputs for general test and environment details
output "workspace" {
  description = "Current Terraform workspace"
  value       = terraform.workspace
}

output "test_prefix" {
  description = "Test prefix used for resources"
  value       = var.test_prefix
}

output "my_ip" {
  description = "Public IP address of the system executing the Terraform plan"
  value       = local.my_ip
}

output "ssh_public_key" {
  description = "SSH public key used for connecting to instances"
  value       = var.ssh_public_key
}

output "ssh_private_key" {
  description = "Derived SSH private key path (assumes standard .pub extension)"
  value       = split(".pub", var.ssh_public_key)[0]
}

output "flavors" {
  value = var.flavors
}
