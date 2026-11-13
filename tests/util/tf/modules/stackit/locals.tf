locals {
  test_name         = replace(var.prefix, "_", "-")
  image_name        = "${local.test_name}-image"
  net_name          = "${local.test_name}-net"
  subnet_name       = "${local.test_name}-subnet"
  fw_name           = "${local.test_name}-sg"
  ssh_key_name      = "${local.test_name}-ssh"
  labels = {
    component  = "gardenlinux"
    test-type  = "platform-test"
    test-name  = local.test_name
  }

  machine_type          = coalesce(var.provider_vars.machine_type,
                            var.image_requirements.arch == "amd64" ? var.instance_type_amd64 :
                            null)
  use_existing_root_disk = var.existing_root_disk != ""
}
