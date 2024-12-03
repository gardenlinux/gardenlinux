output "state_aws_bucket_name" {
  value = var.deploy_state_aws ? module.state_aws.0.bucket_name : null
}

output "test_name" {
  value = local.test_name
}

output "workspace" {
  value = local.workspace
}

# output "git_sha" {
#   value = data.external.git_commit.result.sha
# }
# 
# output "git_sha_short" {
#   value = data.external.git_commit.result.sha_short
# }

output "my_ip" {
  value = local.my_ip
}

output "ssh_public_key" {
  value = var.ssh_public_key
}

output "ssh_private_key" {
  value = split(".pub", var.ssh_public_key).0
}

output "amd64_enabled" {
  value = local.arch_amd64
}

output "arm64_enabled" {
  value = local.arch_arm64
}

output "ali_enabled" {
  value = local.platform_aws
}

output "ali_ssh_user" {
  value = var.ali_ssh_user
}

output "ali_gardener_prod_amd64_public_ip" {
  value = length(module.ali_amd64_default) > 0 ? module.ali_amd64_default.0.public_ip : null
}

output "aws_enabled" {
  value = local.platform_aws
}

output "aws_ssh_user" {
  value = var.aws_ssh_user
}

output "aws_gardener_prod_amd64_public_ip" {
  value = length(module.aws_amd64_default) > 0 ? module.aws_amd64_default.0.public_ip : null
}

output "aws_gardener_prod_arm64_public_ip" {
  value = length(module.aws_arm64_default) > 0 ? module.aws_arm64_default.0.public_ip : null
}

output "aws_gardener_prod_trustedboot_amd64_public_ip" {
  value = length(module.aws_amd64_trustedboot) > 0 ? module.aws_amd64_trustedboot.0.public_ip : null
}

output "aws_gardener_prod_trustedboot_arm64_public_ip" {
  value = length(module.aws_arm64_trustedboot) > 0 ? module.aws_arm64_trustedboot.0.public_ip : null
}

output "aws_gardener_prod_trustedboot_tpm2_amd64_public_ip" {
  value = length(module.aws_amd64_trustedboot_tpm2) > 0 ? module.aws_amd64_trustedboot_tpm2.0.public_ip : null
}

output "aws_gardener_prod_trustedboot_tpm2_arm64_public_ip" {
  value = length(module.aws_arm64_trustedboot_tpm2) > 0 ? module.aws_arm64_trustedboot_tpm2.0.public_ip : null
}

output "azure_enabled" {
  value = local.platform_azure
}

output "azure_ssh_user" {
  value = var.azure_ssh_user
}

output "azure_gardener_prod_amd64_public_ip" {
  value = length(module.azure_amd64_default) > 0 ? module.azure_amd64_default.0.public_ip : null
}

output "azure_gardener_prod_arm64_public_ip" {
  value = length(module.azure_arm64_default) > 0 ? module.azure_arm64_default.0.public_ip : null
}

output "azure_gardener_prod_trustedboot_amd64_public_ip" {
  value = length(module.azure_amd64_trustedboot) > 0 ? module.azure_amd64_trustedboot.0.public_ip : null
}

output "azure_gardener_prod_trustedboot_arm64_public_ip" {
  value = length(module.azure_arm64_trustedboot) > 0 ? module.azure_arm64_trustedboot.0.public_ip : null
}

output "azure_gardener_prod_trustedboot_tpm2_amd64_public_ip" {
  value = length(module.azure_amd64_trustedboot_tpm2) > 0 ? module.azure_amd64_trustedboot_tpm2.0.public_ip : null
}

output "azure_gardener_prod_trustedboot_tpm2_arm64_public_ip" {
  value = length(module.azure_arm64_trustedboot_tpm2) > 0 ? module.azure_arm64_trustedboot_tpm2.0.public_ip : null
}

output "gcp_enabled" {
  value = local.platform_gcp
}

output "gcp_ssh_user" {
  value = var.gcp_ssh_user
}

output "gcp_gardener_prod_amd64_public_ip" {
  value = length(module.gcp_amd64_default) > 0 ? module.gcp_amd64_default.0.public_ip : null
}

output "gcp_gardener_prod_arm64_public_ip" {
  value = length(module.gcp_arm64_default) > 0 ? module.gcp_arm64_default.0.public_ip : null
}

output "gcp_gardener_prod_trustedboot_amd64_public_ip" {
  value = length(module.gcp_amd64_trustedboot) > 0 ? module.gcp_amd64_trustedboot.0.public_ip : null
}

output "gcp_gardener_prod_trustedboot_arm64_public_ip" {
  value = length(module.gcp_arm64_trustedboot) > 0 ? module.gcp_arm64_trustedboot.0.public_ip : null
}

output "gcp_gardener_prod_trustedboot_tpm2_amd64_public_ip" {
  value = length(module.gcp_amd64_trustedboot_tpm2) > 0 ? module.gcp_amd64_trustedboot_tpm2.0.public_ip : null
}

output "gcp_gardener_prod_trustedboot_tpm2_arm64_public_ip" {
  value = length(module.gcp_arm64_trustedboot_tpm2) > 0 ? module.gcp_arm64_trustedboot_tpm2.0.public_ip : null
}
