locals {
  bucket_name = "${var.prefix}-disk-upload"
  ami_name    = "${var.prefix}-image"
  vpc_name    = "${var.prefix}-vpc"
  subnet_name = "${var.prefix}-subnet"
  igw_name    = "${var.prefix}-igw"
  rt_name     = "${var.prefix}-rt"
  sg_name     = "${var.prefix}-sg"
  key_name    = "${var.prefix}-ssh-key"

  root_disk_object_key  = basename(var.root_disk_path)
  test_disk_object_key  = basename(var.test_disk_path)
  default_instance_type = var.image_requirements.arch == "arm64" ? "t4g.medium" : "t3.medium"
  instance_type         = coalesce(var.provider_vars.instance_type, local.default_instance_type)
  default_boot_mode     = var.image_requirements.uefi ? "uefi" : "uefi-preferred"
  boot_mode             = coalesce(var.provider_vars.boot_mode, local.default_boot_mode)
  use_existing_root_disk      = var.existing_root_disk != ""
}
