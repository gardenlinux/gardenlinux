locals {
  test_name            = var.test_name
  test_name_safe       = replace(local.test_name, "_", "-")
  test_name_safe_short = substr(local.test_name_safe, 0, 24)
  feature_tpm2         = contains(var.features, "_tpm2")
  feature_trustedboot  = contains(var.features, "_trustedboot")
  # max 63 chars
  bucket_name = substr("images-${local.test_name_safe}", 0, 63)
  tar_name    = "image-${local.test_name_safe}.tar.gz"
  tar_name_test = "image-test-${local.test_name_safe}.tar.gz"
  image_name  = substr("image-${local.test_name_safe}", 0, 61)
  image_name_test  = substr("image-test-${local.test_name_safe}", 0, 61)
  # max 61 chars
  net_name      = substr("net-${local.test_name_safe}", 0, 61)
  subnet_name   = substr("snet-${local.test_name_safe}", 0, 61)
  sa_name       = "sa-${local.test_name_safe_short}" # can max be 32 chars (now is 27)
  instance_name = "vm-${local.test_name_safe}"
  fw_name       = "fw-${local.test_name_safe}"

  ssh_private_key_file = split(".pub", var.ssh_public_key)[0]
  ssh_parameters       = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"

  public_ip = google_compute_instance.instance.network_interface.0.access_config.0.nat_ip

  image_source_type = split("://", var.image_path)[0]
  image = (
    local.image_source_type == "file" ? "${split("file://", var.image_path)[1]}/${var.image_file}" :
    local.image_source_type == "cloud" ? var.image_file :
    null
  )
  image_test = "/gardenlinux/tests-ng/.build/tests-ng-dist.disk.raw.tar.gz"

  labels = {
    component = "gardenlinux"
    test-type = "platform-test"
    test-name = local.test_name_safe
  }
}

resource "google_storage_bucket" "images" {
  count = 1

  name          = local.bucket_name
  location      = var.region_storage
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  labels = local.labels
}

resource "google_storage_bucket_object" "image" {
  count = local.image_source_type == "file" ? 1 : 0

  name   = local.tar_name
  source = local.image
  bucket = google_storage_bucket.images.0.name

  content_type = "application/x-tar"
}

resource "google_storage_bucket_object" "image_test" {
  count = 1

  name   = local.tar_name_test
  source = local.image_test
  bucket = google_storage_bucket.images.0.name

  content_type = "application/x-tar"
}

# resource "google_service_account" "sa" {
#   account_id   = local.sa_name
#   display_name = "SA for VM Instance"
# }

resource "google_compute_image" "image" {
  count = local.image_source_type == "file" ? 1 : 0

  name = local.image_name

  raw_disk {
    source = "https://storage.cloud.google.com/${google_storage_bucket.images.0.name}/${google_storage_bucket_object.image.0.name}"
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

  dynamic "shielded_instance_initial_state" {
    for_each = local.feature_trustedboot ? [true] : []
    content {
      pk {
        file_type = "X509"
        content   = filebase64("cert/secureboot.pk.der")
      }
      dbs {
        file_type = "X509"
        content   = filebase64("cert/secureboot.db.der")
      }
      keks {
        file_type = "X509"
        content   = filebase64("cert/secureboot.kek.der")
      }
    }
  }

  labels = local.labels

  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.image
    ]
  }
}

resource "google_compute_image" "image_test" {
  count = 1

  name = local.image_name_test

  raw_disk {
    source = "https://storage.cloud.google.com/${google_storage_bucket.images.0.name}/${google_storage_bucket_object.image_test.0.name}"
  }

  labels = local.labels

  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.image_test
    ]
  }
}

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
  target_tags   = [local.test_name_safe]
}

resource "google_compute_disk" "test_disk" {
  name = local.image_name_test
  size = 1
  type = "pd-ssd"
  zone = "${var.region}-${var.zone}"
  image = google_compute_image.image_test.0.self_link
}

resource "google_compute_instance" "instance" {
  name         = local.instance_name
  machine_type = var.instance_type
  zone         = "${var.region}-${var.zone}"

  can_ip_forward = true

  boot_disk {
    initialize_params {
      image = (
        local.image_source_type == "file" ? google_compute_image.image.0.name :
        local.image_source_type == "cloud" ? "projects/sap-se-gcp-gardenlinux/global/images/${local.image}" :
        null
      )
      type  = "pd-ssd"
      size  = 16
    }
  }

  attached_disk {
    source = google_compute_disk.test_disk.self_link
    device_name = "test-disk"
    mode = "READ_WRITE"
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

  metadata_startup_script = file("vm-startup-script.sh")

  ## TODO: evaluate if this is necessary
  # service_account {
  #   # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
  #   email  = google_service_account.sa.email
  #   scopes = ["cloud-platform"]
  # }

  dynamic "shielded_instance_config" {
    for_each = local.feature_trustedboot ? [true] : []
    content {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
      enable_vtpm                 = true
    }
  }

  labels = local.labels

  tags = [
    local.test_name_safe
  ]
}

resource "null_resource" "test_connect" {
  depends_on = [google_compute_instance.instance]

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

resource "null_resource" "test_disk_mount" {
  depends_on = [google_compute_instance.instance]

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
      "sudo mount /dev/disk/by-id/google-test-disk /mnt",
    ]
  }
}
