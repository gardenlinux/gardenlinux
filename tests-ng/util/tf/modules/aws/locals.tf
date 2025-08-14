locals {
  test_name   = replace(var.prefix, "_", "-")
  bucket_name = "${local.test_name}-disk-upload"
  ami_name    = "${local.test_name}-image"
  vpc_name    = "${local.test_name}-vpc"
  subnet_name = "${local.test_name}-subnet"
  igw_name    = "${local.test_name}-igw"
  rt_name     = "${local.test_name}-rt"
  sg_name     = "${local.test_name}-sg"
  key_name    = "${local.test_name}-ssh-key"
  labels = {
    component = "gardenlinux"
    test-type = "platform-test"
    test-name = local.test_name
  }

  root_disk_object_key  = basename(var.root_disk_path)
  test_disk_object_key  = basename(var.test_disk_path)
  default_instance_type = var.image_requirements.arch == "arm64" ? "t4g.medium" : "t3.medium"
  instance_type         = coalesce(var.provider_vars.instance_type, local.default_instance_type)
  default_boot_mode     = var.image_requirements.uefi ? "uefi" : "uefi-preferred"
  boot_mode             = coalesce(var.provider_vars.boot_mode, local.default_boot_mode)
  use_existing_root_disk      = var.existing_root_disk != ""
}
