locals {
  test_name                      = var.test_name
  test_name_safe                 = replace(local.test_name, "_", "-")
  test_name_very_safe            = replace(local.test_name_safe, "-", "")
  test_name_safe_short           = substr(local.test_name_safe, 0, 24)
  arch                           = var.arch == "amd64" ? "x64" : (var.arch == "arm64" ? "Arm64" : null)
  feature_tpm2                   = contains(var.features, "_tpm2")
  feature_trustedboot            = contains(var.features, "_trustedboot")
  resource_group_name            = "rg-${local.test_name}"
  storage_account_name           = lower(replace(substr(strrev(base64encode(local.test_name)), 0, 24), "=", "0")) # only lowercase and max 24 chars
  image_name                     = "image-${local.test_name}.vhd"
  image_gallery_name             = local.test_name_very_safe
  image_gallery_application_name = "gallery-app-${local.test_name}"
  vhds_name                      = substr("vhds-${local.test_name_safe}", 0, 63)
  net_name                       = substr("net-${local.test_name}", 0, 63)
  subnet_name                    = substr("subnet-${local.test_name}", 0, 63)
  pip_name                       = substr("pip-${local.test_name}", 0, 63)
  nic_name                       = substr("nic-${local.test_name}", 0, 63)
  instance_name                  = substr("vm-${local.test_name_safe}", 0, 63)
  fw_name                        = substr("fw-${local.test_name}", 0, 63)
  disk_os_name                   = "disk-os-${local.test_name}"
  ssh_key_name                   = "ssh-${var.ssh_user}-${local.test_name}"
  ssh_private_key_file           = split(".pub", var.ssh_public_key)[0]
  ssh_parameters                 = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"

  public_ip = azurerm_public_ip.pip.ip_address

  image_source_type = split("://", var.image_path)[0]
  image             = local.image_source_type == "file" ? "${split("file://", var.image_path)[1]}/${var.image_file}" : null

  labels = {
    component = "gardenlinux"
    test-type = "platform-test"
    test-name = local.test_name
  }
}

resource "azurerm_resource_group" "rg" {
  location = var.region
  name     = local.resource_group_name

  tags = local.labels
}

resource "azurerm_storage_account" "storage_account" {
  name                = local.storage_account_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  account_tier        = "Standard"
  ## TODO: this is RAGRS in azure.py, do we need that?
  ## https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy#durability-and-availability-parameters
  # account_replication_type = "RAGRS"
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
  name                  = local.vhds_name
  storage_account_id    = azurerm_storage_account.storage_account.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "image" {
  name                   = local.image_name
  storage_account_name   = azurerm_storage_account.storage_account.name
  storage_container_name = azurerm_storage_container.blob.name
  type                   = "Page"
  source                 = local.image

  timeouts {
    create = "4h"
    delete = "30m"
  }
}

resource "azurerm_shared_image_gallery" "gallery" {
  name                = local.image_gallery_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  tags = local.labels
}

resource "azurerm_shared_image" "shared_image" {
  name                = "gardenlinux"
  gallery_name        = azurerm_shared_image_gallery.gallery.name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  hyper_v_generation  = "V2"
  architecture        = local.arch

  trusted_launch_supported = local.feature_trustedboot

  identifier {
    publisher = "Gardenlinux"
    offer     = "Gardenlinux"
    sku       = "Gardenlinux"
  }

  tags = local.labels
}

resource "azurerm_shared_image_version" "shared_image_version" {
  name                = "0.0.0"
  gallery_name        = azurerm_shared_image_gallery.gallery.name
  resource_group_name = azurerm_resource_group.rg.name
  image_name          = azurerm_shared_image.shared_image.name
  location            = azurerm_resource_group.rg.location
  storage_account_id  = azurerm_storage_account.storage_account.id
  blob_uri            = azurerm_storage_blob.image.url
  replication_mode    = "Shallow"

  target_region {
    name                   = azurerm_resource_group.rg.location
    regional_replica_count = 1
    storage_account_type   = "Standard_LRS"
  }

  tags = local.labels

  dynamic "uefi_settings" {
    for_each = local.feature_trustedboot ? [true] : []
    content {
      signature_template_names = [
        "MicrosoftUefiCertificateAuthorityTemplate"
      ]
      additional_signatures {
        db {
          key_type = "x509"
          certificate_data = filebase64("cert/secureboot.db.der")
        }
        kek {
          key_type = "x509"
          certificate_data = filebase64("cert/secureboot.kek.der")
        }
      }
    }
  }
}


# Create virtual network
resource "azurerm_virtual_network" "net" {
  name                = local.net_name
  address_space       = [var.net_range]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = local.labels
}

# Create subnet
resource "azurerm_subnet" "subnet" {
  name                 = local.subnet_name
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.net.name
  address_prefixes     = [var.subnet_range]
}

# Create public IPs
resource "azurerm_public_ip" "pip" {
  name                = local.pip_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  # allocation_method   = "Dynamic"
  allocation_method = "Static"

  tags = local.labels
}

resource "azurerm_network_security_group" "nsg" {
  name                = local.fw_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "${var.my_ip}/32"
    destination_address_prefix = "VirtualNetwork"
  }

  tags = local.labels
}

resource "azurerm_network_interface" "nic" {
  name                = local.nic_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = local.nic_name
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }

  tags = local.labels
}

resource "azurerm_network_interface_security_group_association" "nsg_nic" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# resource "azurerm_subnet_network_security_group_association" "nsg_subnet" {
#   subnet_id = azurerm_subnet.subnet.id
#   network_security_group_id = azurerm_network_security_group.nsg.id
# }

resource "azurerm_ssh_public_key" "ssh_public_key" {
  name                = local.ssh_key_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  public_key          = file(var.ssh_public_key)

  tags = local.labels
}

resource "azurerm_linux_virtual_machine" "instance" {
  name                  = local.instance_name
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.nic.id]
  size                  = var.instance_type

  source_image_id = azurerm_shared_image_version.shared_image_version.id

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }

  computer_name = local.instance_name
  custom_data   = filebase64("vm-startup-script.sh")

  disable_password_authentication = true
  admin_username                  = var.ssh_user
  admin_ssh_key {
    username   = var.ssh_user
    public_key = azurerm_ssh_public_key.ssh_public_key.public_key
  }

  boot_diagnostics {
    storage_account_uri = azurerm_storage_account.storage_account.primary_blob_endpoint
  }

  secure_boot_enabled = local.feature_trustedboot
  vtpm_enabled        = local.feature_trustedboot

  tags = local.labels

  # wait until image version is available
  depends_on = [
    azurerm_shared_image_version.shared_image_version
  ]

  # replace if image source changes
  lifecycle {
    replace_triggered_by = [
      azurerm_storage_blob.image.metadata
    ]
  }
}

resource "null_resource" "test_connect" {
  depends_on = [azurerm_linux_virtual_machine.instance]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(split(".pub", var.ssh_public_key)[0])
      host        = local.public_ip
      # usually this is created in /tmp but we have it mounted noexec
      script_path = "/home/${var.ssh_user}/terraform_%RAND%.sh"
      timeout     = "10m"
    }

    inline = [
      "cat /etc/os-release",
    ]
  }
}
