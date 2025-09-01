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

resource "azurerm_storage_account" "storage_account" {
  name                = local.bucket_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  account_tier        = "Standard"
  account_replication_type = "LRS"

  https_traffic_only_enabled = true
  min_tls_version            = "TLS1_2"

  network_rules {
    default_action = "Deny"
    ip_rules = [
      var.my_ip,
      ## TODO: make serial console work
      # serial console service IPs for North/West Europe and Germany
      # https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/linux/serial-console-linux#use-serial-console-with-custom-boot-diagnostics-storage-account-firewall-enabled
      # "52.146.139.220",
      # "20.105.209.72",
      # "51.116.75.88",
      # "20.52.95.48"
    ]
  }

  # The tag enables ignoring the policy that blocks public access.
  # This is fine as we only allow the IP address that uploads the image.
  public_network_access_enabled = true
  tags                          = merge(local.labels, { sec-by-def-public-storage-exception = "enabled" })
}

resource "azurerm_storage_container" "blob" {
  count = var.existing_root_disk != "" ? 0 : 1

  name                  = local.image_name
  storage_account_id    = azurerm_storage_account.storage_account.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "image" {
  count = var.existing_root_disk != "" ? 0 : 1

  name                   = local.image_name
  storage_account_name   = azurerm_storage_account.storage_account.name
  storage_container_name = azurerm_storage_container.blob.0.name
  type                   = "Page"
  source = replace(var.root_disk_path, ".raw", ".vhd")

  timeouts {
    create = "4h"
    delete = "30m"
  }

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash
    ]
  }
}

resource "azurerm_shared_image_gallery" "gallery" {
  count = var.existing_root_disk != "" ? 0 : 1

  name                = local.bucket_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  tags = local.labels
}

resource "azurerm_shared_image" "shared_image" {
  count = var.existing_root_disk != "" ? 0 : 1

  name                = "gardenlinux"
  gallery_name        = azurerm_shared_image_gallery.gallery.0.name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  hyper_v_generation  = "V2"
  architecture        = local.arch

  trusted_launch_supported = var.image_requirements.secureboot

  identifier {
    publisher = "Gardenlinux"
    offer     = "Gardenlinux"
    sku       = "Gardenlinux"
  }

  tags = local.labels
}

resource "azurerm_shared_image_version" "shared_image_version" {
  count = var.existing_root_disk != "" ? 0 : 1

  name                = "0.0.0"
  gallery_name        = azurerm_shared_image_gallery.gallery.0.name
  resource_group_name = azurerm_resource_group.rg.name
  image_name          = azurerm_shared_image.shared_image.0.name
  location            = azurerm_resource_group.rg.location
  storage_account_id  = azurerm_storage_account.storage_account.id
  blob_uri            = azurerm_storage_blob.image.0.url
  replication_mode    = "Shallow"

  target_region {
    name                   = azurerm_resource_group.rg.location
    regional_replica_count = 1
    storage_account_type   = "Standard_LRS"
  }

  tags = local.labels


  dynamic "uefi_settings" {
    for_each = var.image_requirements.secureboot ? [true] : []
    content {
      signature_template_names = [
        "MicrosoftUefiCertificateAuthorityTemplate"
      ]
      additional_signatures {
        db {
          type = "x509"
          certificate_base64 = [ filebase64("cert/secureboot.db.der") ]
        }
        kek {
          type = "x509"
          certificate_base64 = [ filebase64("cert/secureboot.kek.der") ]
        }
      }
    }
  }
}
resource "azurerm_storage_blob" "image_test" {
  name = "${local.image_name}-test"
  storage_account_name   = azurerm_storage_account.storage_account.name
  storage_container_name = azurerm_storage_container.blob.0.name
  type                   = "Page"
  source = replace(var.test_disk_path, ".raw", ".vhd")

  timeouts {
    create = "4h"
    delete = "30m"
  }

  lifecycle {
    replace_triggered_by = [
      terraform_data.test_disk_hash
    ]
  }
}

resource "azurerm_managed_disk" "test_disk" {
  name = "${local.image_name}-test"
  location             = azurerm_resource_group.rg.location
  resource_group_name  = azurerm_resource_group.rg.name
  storage_account_type = "StandardSSD_LRS"
  create_option        = "Import"
  disk_size_gb         = 1
  source_uri           = azurerm_storage_blob.image_test.url
  storage_account_id   = azurerm_storage_account.storage_account.id

  tags = local.labels
}

resource "azurerm_virtual_machine_data_disk_attachment" "test_disk_attachment" {
  managed_disk_id    = azurerm_managed_disk.test_disk.id
  virtual_machine_id = azurerm_linux_virtual_machine.instance.id
  lun                = "10"
  caching            = "ReadWrite"
}
