locals {
  workspace   = terraform.workspace != "default" ? terraform.workspace : local.test_suffix
  test_suffix = var.flavor != null ? "${var.flavor}" : ""
  test_name   = "${var.test_prefix}-${local.workspace}"

  my_ip = data.external.my_ip.result.ip

  # platforms
  platform_ali   = contains(var.platforms, "ali")
  platform_aws   = contains(var.platforms, "aws")
  platform_azure = contains(var.platforms, "azure")
  platform_gcp   = contains(var.platforms, "gcp")

  # archs
  arch_amd64 = contains(var.archs, "amd64")
  arch_arm64 = contains(var.archs, "arm64")

  # features
  feature_default     = var.features == []
  feature_tpm2        = contains(var.features, "_tpm2")
  feature_trustedboot = contains(var.features, "_trustedboot")
}

provider "alicloud" {
  region = var.ali_region
}

provider "aws" {
  region = var.aws_region
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# data "external" "git_commit" {
#   program = [
#     "git",
#     "log",
#     "--pretty=format:{ \"sha\": \"%H\", \"sha_short\": \"%h\" }",
#     "-1",
#     "HEAD"
#   ]
# }

data "external" "my_ip" {
  program = ["curl", "-q", "https://api.ipify.org?format=json"]
}

module "ali_amd64_default" {
  source = "./modules/ali"

  count = local.platform_ali && local.arch_amd64 && local.feature_default ? 1 : 0

  arch           = "amd64"
  features       = []
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.ali_image_file
  ssh_user   = var.ali_ssh_user

  region        = var.ali_region
  instance_type = var.ali_instance_type
}

module "aws_amd64_default" {
  source = "./modules/aws"

  count = local.platform_aws && local.arch_amd64 && local.feature_default ? 1 : 0

  arch           = "amd64"
  features       = []
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.aws_image_file
  ssh_user   = var.aws_ssh_user

  region        = var.aws_region
  instance_type = var.aws_instance_type
}

module "aws_amd64_trustedboot" {
  source = "./modules/aws"

  count = local.platform_aws && local.arch_amd64 && local.feature_trustedboot && !local.feature_tpm2 ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.aws_image_file
  ssh_user   = var.aws_ssh_user

  region        = var.aws_region
  instance_type = var.aws_instance_type
}

module "aws_amd64_trustedboot_tpm2" {
  source = "./modules/aws"

  count = local.platform_aws && local.arch_amd64 && local.feature_trustedboot && local.feature_tpm2 ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.aws_image_file
  ssh_user   = var.aws_ssh_user

  region        = var.aws_region
  instance_type = var.aws_instance_type
}

module "aws_arm64_default" {
  source = "./modules/aws"

  count = local.platform_aws && local.arch_arm64 && local.feature_default ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.aws_image_file
  ssh_user   = var.aws_ssh_user

  region        = var.aws_region
  instance_type = var.aws_instance_type
}

module "aws_arm64_trustedboot" {
  source = "./modules/aws"

  count = local.platform_aws && local.arch_arm64 && local.feature_trustedboot && !local.feature_tpm2 ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.aws_image_file
  ssh_user   = var.aws_ssh_user

  region        = var.aws_region
  instance_type = var.aws_instance_type
}

module "aws_arm64_trustedboot_tpm2" {
  source = "./modules/aws"

  count = local.platform_aws && local.arch_arm64 && local.feature_trustedboot && local.feature_tpm2 ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.aws_image_file
  ssh_user   = var.aws_ssh_user

  region        = var.aws_region
  instance_type = var.aws_instance_type
}

module "azure_amd64_default" {
  source = "./modules/azure"

  count = local.platform_azure && local.arch_amd64 && local.feature_default ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.azure_image_file
  ssh_user   = var.azure_ssh_user

  region        = var.azure_region
  instance_type = var.azure_instance_type
}

module "azure_amd64_trustedboot" {
  source = "./modules/azure"

  count = local.platform_azure && local.arch_amd64 && local.feature_trustedboot && !local.feature_tpm2 ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.azure_image_file
  ssh_user   = var.azure_ssh_user

  region        = var.azure_region
  instance_type = var.azure_instance_type
}

module "azure_amd64_trustedboot_tpm2" {
  source = "./modules/azure"

  count = local.platform_azure && local.arch_amd64 && local.feature_trustedboot && local.feature_tpm2 ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.azure_image_file
  ssh_user   = var.azure_ssh_user

  region        = var.azure_region
  instance_type = var.azure_instance_type
}

module "azure_arm64_default" {
  source = "./modules/azure"

  count = local.platform_azure && local.arch_arm64 && local.feature_default ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.azure_image_file
  ssh_user   = var.azure_ssh_user

  region        = var.azure_region
  instance_type = var.azure_instance_type
}

module "azure_arm64_trustedboot" {
  source = "./modules/azure"

  count = local.platform_azure && local.arch_arm64 && local.feature_trustedboot && !local.feature_tpm2 ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.azure_image_file
  ssh_user   = var.azure_ssh_user

  region        = var.azure_region
  instance_type = var.azure_instance_type
}

module "azure_arm64_trustedboot_tpm2" {
  source = "./modules/azure"

  count = local.platform_azure && local.arch_arm64 && local.feature_trustedboot && local.feature_tpm2 ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.azure_image_file
  ssh_user   = var.azure_ssh_user

  region        = var.azure_region
  instance_type = var.azure_instance_type
}

module "gcp_amd64_default" {
  source = "./modules/gcp"

  count = local.platform_gcp && local.arch_amd64 && local.feature_default ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.gcp_image_file
  ssh_user   = var.gcp_ssh_user

  project_id     = var.gcp_project_id
  region         = var.gcp_region
  region_storage = var.gcp_region_storage
  zone           = var.gcp_zone
  instance_type  = var.gcp_instance_type
}

module "gcp_amd64_trustedboot" {
  source = "./modules/gcp"

  count = local.platform_gcp && local.arch_amd64 && local.feature_trustedboot && !local.feature_tpm2 ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.gcp_image_file
  ssh_user   = var.gcp_ssh_user

  project_id     = var.gcp_project_id
  region         = var.gcp_region
  region_storage = var.gcp_region_storage
  zone           = var.gcp_zone
  instance_type  = var.gcp_instance_type
}

module "gcp_amd64_trustedboot_tpm2" {
  source = "./modules/gcp"

  count = local.platform_gcp && local.arch_amd64 && local.feature_trustedboot && local.feature_tpm2 ? 1 : 0

  arch           = "amd64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.gcp_image_file
  ssh_user   = var.gcp_ssh_user

  project_id     = var.gcp_project_id
  region         = var.gcp_region
  region_storage = var.gcp_region_storage
  zone           = var.gcp_zone
  instance_type  = var.gcp_instance_type
}

module "gcp_arm64_default" {
  source = "./modules/gcp"

  count = local.platform_gcp && local.arch_arm64 && local.feature_default ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.gcp_image_file
  ssh_user   = var.gcp_ssh_user

  project_id     = var.gcp_project_id
  region         = var.gcp_region
  region_storage = var.gcp_region_storage
  zone           = var.gcp_zone
  instance_type  = var.gcp_instance_type
}

module "gcp_arm64_trustedboot" {
  source = "./modules/gcp"

  count = local.platform_gcp && local.arch_arm64 && local.feature_trustedboot && !local.feature_tpm2 ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.gcp_image_file
  ssh_user   = var.gcp_ssh_user

  project_id     = var.gcp_project_id
  region         = var.gcp_region
  region_storage = var.gcp_region_storage
  zone           = var.gcp_zone
  instance_type  = var.gcp_instance_type
}

module "gcp_arm64_trustedboot_tpm2" {
  source = "./modules/gcp"

  count = local.platform_gcp && local.arch_arm64 && local.feature_trustedboot && local.feature_tpm2 ? 1 : 0

  arch           = "arm64"
  features       = var.features
  test_name      = local.test_name
  image_path     = var.image_path
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = local.my_ip

  image_file = var.gcp_image_file
  ssh_user   = var.gcp_ssh_user

  project_id     = var.gcp_project_id
  region         = var.gcp_region
  region_storage = var.gcp_region_storage
  zone           = var.gcp_zone
  instance_type  = var.gcp_instance_type
}

module "state_aws" {
  source = "./modules/state_aws"

  count            = var.deploy_state_aws ? 1 : 0
  test_name        = local.test_name
  test_environment = var.test_environment
}

# module "state_aws_kms" {
#   source = "./modules/state_aws_kms"
# 
#   count = var.deploy_state_aws_kms ? 1 : 0
#   test_name      = local.test_name
# }
