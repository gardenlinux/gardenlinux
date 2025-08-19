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

resource "google_storage_bucket" "images" {
  count = var.existing_root_disk != "" ? 0 : 1

  name          = local.bucket_name
  location      = var.provider_vars.region_storage
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  labels = local.labels
}

resource "google_storage_bucket_object" "image" {
  count = var.existing_root_disk != "" ? 0 : 1

  name   = replace(local.root_disk_object_key, ".raw", ".gcpimage.tar.gz")
  source = replace(var.root_disk_path, ".raw", ".gcpimage.tar.gz")

  bucket = google_storage_bucket.images.0.name

  content_type = "application/x-tar"
}

resource "google_compute_image" "image" {
  count = var.existing_root_disk != "" ? 0 : 1

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

  # dynamic "shielded_instance_initial_state" {
  #   for_each = local.feature_trustedboot ? [true] : []
  #   content {
  #     pk {
  #       file_type = "X509"
  #       content   = filebase64("cert/secureboot.pk.der")
  #     }
  #     dbs {
  #       file_type = "X509"
  #       content   = filebase64("cert/secureboot.db.der")
  #     }
  #     keks {
  #       file_type = "X509"
  #       content   = filebase64("cert/secureboot.kek.der")
  #     }
  #   }
  # }

  labels = local.labels

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash
    ]
  }
}

resource "google_storage_bucket_object" "image_test" {
  name   = replace(local.test_disk_object_key, ".raw", ".raw.tar.gz")
  source = replace(var.test_disk_path, ".raw", ".raw.tar.gz")
  bucket = google_storage_bucket.images.0.name

  content_type = "application/x-tar"
}

resource "google_compute_image" "image_test" {
  name = "${local.image_name}-test"

  raw_disk {
    source = "https://storage.cloud.google.com/${google_storage_bucket.images.0.name}/${google_storage_bucket_object.image_test.name}"
  }

  labels = local.labels

  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.image_test
    ]
  }
}

resource "google_compute_disk" "test_disk" {
  name = "${local.image_name}-test"
  size = 1
  type = "pd-ssd"
  zone = "${var.provider_vars.region}-${var.provider_vars.zone}"
  image = google_compute_image.image_test.self_link
}
