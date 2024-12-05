locals {
  seed = terraform.workspace != "default" ? regex(".*-(.*)$", terraform.workspace)[0] : "00000000"

  my_ip = data.external.my_ip.result.ip

  # Generate module_config based on flavors
  module_config = [
    for flavor in var.flavors : {
      name        = flavor.name
      name_unique = "${var.test_prefix}-${flavor.name}-${local.seed}"
      platform    = flavor.platform
      features    = flavor.features
      arch        = flavor.arch
      seed        = local.seed
      instance_type = try(flavor.instance_type, lookup(
        {
          "ali"   = var.ali_instance_type,
          "aws"   = var.aws_instance_type,
          "azure" = var.azure_instance_type,
          "gcp"   = var.gcp_instance_type
        },
        flavor.platform,
        null
      ))
      image_file = try(flavor.image_file, lookup(
        {
          "ali"   = var.ali_image_file,
          "aws"   = var.aws_image_file,
          "azure" = var.azure_image_file,
          "gcp"   = var.gcp_image_file
        },
        flavor.platform,
        null
      ))
      ssh_user = try(flavor.ssh_user, lookup(
        {
          "ali"   = var.ali_ssh_user,
          "aws"   = var.aws_ssh_user,
          "azure" = var.azure_ssh_user,
          "gcp"   = var.gcp_ssh_user
        },
        flavor.platform,
        null
      ))
      region = try(flavor.region, lookup(
        {
          "ali"   = var.ali_region,
          "aws"   = var.aws_region,
          "azure" = var.azure_region,
          "gcp"   = var.gcp_region
        },
        flavor.platform,
        null
      ))
      # provider specific variables
      region_storage = try(flavor.region_storage, lookup(
        {
          "gcp" = var.gcp_region_storage,
        },
        flavor.platform,
        null
      ))
      account = lookup(
        {
          "gcp" = var.gcp_project_id
        },
        flavor.platform,
        null
      )
      zone = try(flavor.zone, lookup(
        {
          "gcp" = var.gcp_zone,
        },
        flavor.platform,
        null
      ))
    }
  ]
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

data "external" "my_ip" {
  program = ["curl", "-q", "https://api.ipify.org?format=json"]
}

module "ali" {
  for_each = { for config in local.module_config : config.name => config if config.platform == "ali" }

  source = "./modules/ali"

  arch           = each.value.arch
  features       = each.value.features
  test_name      = each.value.name_unique
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = data.external.my_ip.result.ip

  image_file    = each.value.image_file
  ssh_user      = each.value.ssh_user
  region        = each.value.region
  instance_type = each.value.instance_type
}

module "aws" {
  for_each = { for config in local.module_config : config.name => config if config.platform == "aws" }

  source = "./modules/aws"

  arch           = each.value.arch
  features       = each.value.features
  test_name      = each.value.name_unique
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = data.external.my_ip.result.ip

  image_file    = each.value.image_file
  ssh_user      = each.value.ssh_user
  region        = each.value.region
  instance_type = each.value.instance_type
}

module "azure" {
  for_each = { for config in local.module_config : config.name => config if config.platform == "azure" }

  source = "./modules/azure"

  arch           = each.value.arch
  features       = each.value.features
  test_name      = each.value.name_unique
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = data.external.my_ip.result.ip

  image_file    = each.value.image_file
  ssh_user      = each.value.ssh_user
  region        = each.value.region
  instance_type = each.value.instance_type
}

module "gcp" {
  for_each = { for config in local.module_config : config.name => config if config.platform == "gcp" }

  source = "./modules/gcp"

  arch           = each.value.arch
  features       = each.value.features
  test_name      = each.value.name_unique
  image_path     = var.image_path
  net_range      = var.net_range
  subnet_range   = var.subnet_range
  ssh_public_key = var.ssh_public_key
  my_ip          = data.external.my_ip.result.ip

  image_file    = each.value.image_file
  ssh_user      = each.value.ssh_user
  region        = each.value.region
  instance_type = each.value.instance_type

  # provider specific
  region_storage = each.value.region_storage
  zone           = each.value.zone
  project_id     = each.value.account
}



module "state_aws" {
  source = "./modules/state_aws"

  count            = var.deploy_state_aws ? 1 : 0
  test_name        = var.test_prefix
  test_environment = var.test_environment
}

# module "state_aws_kms" {
#   source = "./modules/state_aws_kms"
# 
#   count = var.deploy_state_aws_kms ? 1 : 0
#   test_name      = local.test_name
# }
