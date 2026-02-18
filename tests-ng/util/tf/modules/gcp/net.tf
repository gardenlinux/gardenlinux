resource "google_compute_network" "network" {
  name                    = local.net_name
  auto_create_subnetworks = false
  mtu                     = 1460
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "subnetwork" {
  name                     = local.subnet_name
  ip_cidr_range            = var.provider_vars.subnet_cidr
  region                   = var.provider_vars.region
  network                  = google_compute_network.network.id
  private_ip_google_access = false
}

resource "google_compute_firewall" "firewall" {
  name        = local.fw_name
  description = "allow incoming SSH and ICMP for Garden Linux integration tests"
  network     = google_compute_network.network.name

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = [var.my_ip]
  target_tags   = [local.test_name]
}
