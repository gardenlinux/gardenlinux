resource "azurerm_resource_group" "rg" {
  location = var.provider_vars.region
  name     = local.test_name

  tags = local.labels
}
