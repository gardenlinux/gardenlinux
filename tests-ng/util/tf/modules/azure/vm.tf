resource "azurerm_ssh_public_key" "ssh_public_key" {
  name                = local.ssh_key_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  public_key          = file(var.ssh_public_key_path)

  tags = local.labels
}

resource "azurerm_linux_virtual_machine" "instance" {
  name                  = local.test_name
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.nic.id]
  size                  = local.instance_type

  source_image_id = (
    var.existing_root_disk != "" ? basename(var.root_disk_path) :
    var.existing_root_disk == "" ? azurerm_shared_image_version.shared_image_version.0.id :
    null
  )

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 16
  }

  computer_name = local.test_name
  custom_data   = filebase64(var.user_data_script_path)

  disable_password_authentication = true
  admin_username                  = var.provider_vars.ssh_user
  admin_ssh_key {
    username   = var.provider_vars.ssh_user
    public_key = azurerm_ssh_public_key.ssh_public_key.public_key
  }

  boot_diagnostics {
    storage_account_uri = azurerm_storage_account.storage_account.primary_blob_endpoint
  }

  # secure_boot_enabled = local.feature_trustedboot
  # vtpm_enabled        = local.feature_trustedboot

  tags = local.labels

  # wait until image version and nic are available
  depends_on = [
    azurerm_shared_image_version.shared_image_version.0,
    azurerm_network_interface.nic
  ]

  # replace if image source changes
  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash,
      terraform_data.test_disk_hash,
    ]
  }
}

output "vm_ip" {
  value       = azurerm_linux_virtual_machine.instance.public_ip_address
  description = "Public IPv4 of the VM"
}

output "ssh_user" {
  value       = var.provider_vars.ssh_user
}
