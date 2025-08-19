resource "terraform_data" "root_disk_hash" {
  count = var.existing_root_disk != "" ? 0 : 1
  input = {
    sha256 = filesha256(var.root_disk_path)
  }
}

resource "terraform_data" "test_disk_hash" {
  count = var.use_scp ? 0 : 1
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

### # GCP does not support plain raw disks as images, so we need to create a tar.gz file that contains a file called disk.raw
### resource "terraform_data" "test_disk_tar" {
###   count = var.use_scp ? 0 : 1
###   input = {
###     source_path = var.test_disk_path
###     tar_path    = replace(var.test_disk_path, ".raw", ".raw.tar.gz")
###   }
### }
###
### resource "null_resource" "create_test_disk_tar" {
###   count = var.use_scp ? 0 : 1
###
###   triggers = {
###     disk_hash = terraform_data.test_disk_hash[0].output.sha256
###   }
###
###   provisioner "local-exec" {
###     command = "cd '${dirname(var.test_disk_path)}' && cp '${basename(var.test_disk_path)}' 'disk.raw' && tar -czf '${basename(terraform_data.test_disk_tar[0].output.tar_path)}' 'disk.raw' && rm 'disk.raw'"
###   }
### }

resource "google_storage_bucket_object" "image_test" {
  count = var.use_scp ? 0 : 1

  name   = replace(local.test_disk_object_key, ".raw", ".raw.tar.gz")
  source = replace(var.test_disk_path, ".raw", ".raw.tar.gz")
  bucket = google_storage_bucket.images.0.name

  content_type = "application/x-tar"

  depends_on = [null_resource.create_test_disk_tar]
}

resource "google_compute_image" "image_test" {
  count = var.use_scp ? 0 : 1

  name = "${local.image_name}-test"

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

resource "google_compute_disk" "test_disk" {
  count = var.use_scp ? 0 : 1

  name = "${local.image_name}-test"
  size = 1
  type = "pd-ssd"
  zone = "${var.provider_vars.region}-${var.provider_vars.zone}"
  image = google_compute_image.image_test.0.self_link
}
