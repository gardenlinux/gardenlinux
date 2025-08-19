resource "google_compute_instance" "instance" {
  name         = local.test_name
  machine_type = local.instance_type
  zone         = "${var.provider_vars.region}-${var.provider_vars.zone}"

  can_ip_forward = true

  boot_disk {
    initialize_params {
      # image = (
      #   local.image_source_type == "file" ? google_compute_image.image.0.name :
      #   local.image_source_type == "cloud" ? "projects/sap-se-gcp-gardenlinux/global/images/${local.image}" :
      #   null
      # )
      image = google_compute_image.image.0.name
      type  = "pd-ssd"
      size  = 16
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnetwork.id

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "${var.provider_vars.ssh_user}:${file(var.ssh_public_key_path)}"
  }

  metadata_startup_script = file(var.user_data_script_path)

  ## TODO: secure boot
  # dynamic "shielded_instance_config" {
  #   for_each = local.feature_trustedboot ? [true] : []
  #   content {
  #     enable_secure_boot          = true
  #     enable_integrity_monitoring = true
  #     enable_vtpm                 = true
  #   }
  # }

  attached_disk {
    source = google_compute_disk.test_disk.self_link
    device_name = "test-disk"
    mode = "READ_WRITE"
  }

  labels = local.labels

  tags = [
    local.test_name
  ]

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash,
      terraform_data.test_disk_hash,
    ]
  }
}

output "vm_ip" {
  value       = google_compute_instance.instance.network_interface[0].access_config[0].nat_ip
  description = "Public IPv4 of the VM"
}

output "ssh_user" {
  value       = var.provider_vars.ssh_user
}
