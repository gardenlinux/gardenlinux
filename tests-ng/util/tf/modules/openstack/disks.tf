resource "terraform_data" "root_disk_hash" {
  count = var.existing_root_disk != "" ? 0 : 1
  input = {
    sha256 = filesha256(var.root_disk_path)
  }
}

resource "terraform_data" "test_disk_hash" {
  input = {
    sha256 = filesha256(var.test_disk_path)
  }

}

resource "openstack_images_image_v2" "image" {
  name = local.image_name
  local_file_path = var.root_disk_path
  container_format = "bare"
  disk_format = "raw"
  min_disk_gb = 3
  min_ram_mb = 512
  properties = {
    architecture = local.arch
    cpu_arch = local.arch
    hypervisor_type = "qemu"
    image_description = "Garden Linux Platform Test"
    distro = "gardenlinux"
    os_distro = "gardenlinux"
    os_admin_user = var.provider_vars.ssh_user
    # setting this to "required" will give us "nova.exception.SecureBootNotSupported: Secure Boot is not supported by host"
    os_secure_boot = var.image_requirements.secureboot ? "optional" : null
    # setting a NVRAM template could be an option to boot with different OVMF_VARS.fd with PK/DB/DBX/KEK
    # this is undocumented and not working as of OpenStack 2024.1
    # the OVMF_VARS.fd and template would have to exist on the nova compute node
    # os_nvram_template = local.feature_trustedboot ? "/usr/share/qemu/firmware/99-edk2-x86_64-secure-enrolled-gl.json" : null
    hw_firmware_type = "uefi"
    hw_tpm_version = var.image_requirements.tpm2 ? "2.0" : null
    hw_tpm_model= var.image_requirements.tpm2 ? "tpm-tis" : null
  }

  timeouts {
    create = "2h"
  }
}

resource "openstack_images_image_v2" "test_disk" {
  name = "${local.image_name}-test-disk"
  local_file_path = var.test_disk_path
  container_format = "bare"
  disk_format = "raw"
  min_disk_gb = 1
  min_ram_mb = 512
  properties = {
    image_description = "Garden Linux Platform Test Disk"
  }

  timeouts {
    create = "2h"
  }
}

resource "openstack_blockstorage_volume_v3" "test_disk" {
  name = "${local.image_name}-test-volume"
  size = 1
  image_id = openstack_images_image_v2.test_disk.id
}

resource "openstack_compute_volume_attach_v2" "test_disk" {
  instance_id = openstack_compute_instance_v2.instance.id
  volume_id = openstack_blockstorage_volume_v3.test_disk.id
}
