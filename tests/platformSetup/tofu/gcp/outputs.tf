output "platform" {
  value = var.platform
}
output "test_name" {
  value = var.test_name
}
output "test_uuid" {
  value = local.uuid
}
output "public_ip" {
  value = google_compute_instance.instance.network_interface.0.access_config.0.nat_ip
}
