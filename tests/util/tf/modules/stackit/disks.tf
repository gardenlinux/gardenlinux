resource "terraform_data" "root_disk_hash" {
  input = {
    sha256 = local.use_existing_root_disk ? "existing" : filesha256(var.root_disk_path)
  }
}

resource "terraform_data" "test_disk_hash" {
  input = {
    sha256 = filesha256(var.test_disk_path)
  }
}

resource "stackit_image" "image" {
  count = local.use_existing_root_disk ? 0 : 1

  project_id      = var.provider_vars.project_id
  name            = local.image_name
  local_file_path = var.root_disk_path
  disk_format     = "raw"

  labels = local.labels
}

resource "stackit_image" "test_disk" {
  count = var.skip_tests ? 0 : 1

  project_id      = var.provider_vars.project_id
  name            = "${local.image_name}-test-disk"
  local_file_path = var.test_disk_path
  disk_format     = "raw"

  labels = local.labels
}

resource "stackit_volume" "test_disk" {
  count = var.skip_tests ? 0 : 1

  project_id        = var.provider_vars.project_id
  name              = "${local.test_name}-test-volume"
  availability_zone = var.provider_vars.availability_zone
  size              = 1

  source = {
    type = "image"
    id   = stackit_image.test_disk[0].image_id
  }

  labels = local.labels
}

resource "stackit_server_volume_attach" "test_disk" {
  count = var.skip_tests ? 0 : 1

  project_id = var.provider_vars.project_id
  server_id  = stackit_server.instance.server_id
  volume_id  = stackit_volume.test_disk[0].volume_id
}
