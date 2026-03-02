data "alicloud_account" "current" {
}

data "alicloud_caller_identity" "current" {
}

data "alicloud_zones" "zones" {
  available_resource_creation = "VSwitch"
}
