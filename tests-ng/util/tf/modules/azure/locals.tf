locals {
  test_name   = replace(var.prefix, "_", "-")
  # lowercase alphanumeric string (max 24 chars), with dashes and non-alphanumeric characters removed
  bucket_name = substr(lower(replace(replace("${local.test_name}-images", "-", ""), "/[^a-z0-9]/", "")), 0, 24)
  image_name    = "${local.test_name}-image"
  net_name    = "${local.test_name}-net"
  subnet_name = "${local.test_name}-subnet"
  igw_name    = "${local.test_name}-igw"
  route_table_name     = "${local.test_name}-rt"
  fw_name     = "${local.test_name}-fw"
  ssh_key_name    = "${local.test_name}-ssh"
  labels = {
    component = "gardenlinux"
    test-type = "platform-test"
    test-name = local.test_name
  }

  arch = var.image_requirements.arch == "amd64" ? "x64" : var.image_requirements.arch == "arm64" ? "Arm64" : null
  root_disk_object_key  = basename(var.root_disk_path)
  test_disk_object_key  = basename(var.test_disk_path)
  instance_type         = coalesce(var.provider_vars.instance_type,
                            var.image_requirements.arch == "amd64" ? var.instance_type_amd64 :
                            var.image_requirements.arch == "arm64" ? var.instance_type_arm64 :
                            null)
  default_boot_mode     = var.image_requirements.uefi ? "uefi" : "uefi-preferred"
  boot_mode             = coalesce(var.provider_vars.boot_mode, local.default_boot_mode)
  use_existing_root_disk      = var.existing_root_disk != ""
}
