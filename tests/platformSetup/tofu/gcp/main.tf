provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  uuid = uuid()
  bucket_name   = "images-${var.test_name}"
  tar_name      = "image-${var.test_name}.tar.gz"
  image_name    = "image-${var.test_name}"
  net_name      = "net-${var.test_name}"
  subnet_name   = "subnet-${var.test_name}"
  sa_name       = "sa-${var.test_name}"
  instance_name = "instance-${var.test_name}"
  fw_name = "fw-${var.test_name}"
}

resource "google_storage_bucket" "images" {
  name          = local.bucket_name
  location      = var.region_storage
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

resource "google_storage_bucket_object" "image" {
  name   = local.tar_name
  source = var.image_source
  bucket = google_storage_bucket.images.name

  content_type = "application/x-tar"
}

resource "google_service_account" "sa" {
  account_id   = local.sa_name
  display_name = "SA for VM Instance"
}

resource "google_compute_image" "image" {
  name = local.image_name

  raw_disk {
    source = "https://storage.cloud.google.com/${google_storage_bucket.images.name}/${google_storage_bucket_object.image.name}"
  }

  guest_os_features {
    type = "VIRTIO_SCSI_MULTIQUEUE"
  }
  guest_os_features {
    type = "UEFI_COMPATIBLE"
  }
  guest_os_features {
    type = "GVNIC"
  }
  # guest_os_features {
  #   type = "SECURE_BOOT"
  # }
}

# self._tags = {
#     "component": "gardenlinux",
#     "test-type": "integration-test",
#     "test-name": self.test_name,
#     "test-uuid": str(uuid.uuid4()),
# }

resource "google_compute_network" "network" {
  name                    = local.net_name
  auto_create_subnetworks = false
  mtu                     = 1460
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "subnetwork" {
  name                     = local.subnet_name
  ip_cidr_range            = var.subnet_range
  region                   = var.region
  network                  = google_compute_network.network.id
  private_ip_google_access = false
}

resource "google_compute_firewall" "firewall" {
  name    = local.fw_name
  description = "allow incoming SSH and ICMP for Garden Linux integration tests"
  network = google_compute_network.network.name

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  # source_ranges = [google_compute_instance.instance.network_interface.0.access_config.0.nat_ip]
  # source_ranges = ["35.235.240.0/20"]
  target_tags = [var.test_name]
}

resource "google_compute_network" "default" {
  name = "test-network"
}

resource "google_compute_instance" "instance" {
  name         = local.instance_name
  machine_type = var.instance_type
  zone         = "${var.region}-${var.zone}"

  can_ip_forward = true

  boot_disk {
    initialize_params {
      # image = "debian-cloud/debian-11"
      image = google_compute_image.image.name
      type  = "pd-ssd"
      size  = 7
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnetwork.id

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.ssh_public_key)}"
  }

  metadata_startup_script = "touch /tmp/startup-script-ok && systemctl start ssh"

  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.sa.email
    scopes = ["cloud-platform"]
  }

  labels = {
    component =  "gardenlinux"
    test-type =  "platform-test"
    test-name =  var.test_name
    test-uuid =  local.uuid
  }

  tags = [
    var.test_name
  ]
}
