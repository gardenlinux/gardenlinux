resource "terraform_data" "root_disk_hash" {
  input = {
    sha256 = filesha256(var.root_disk_path)
  }
}

resource "terraform_data" "test_disk_hash" {
  input = {
    sha256 = filesha256(var.test_disk_path)
  }
}

resource "aws_s3_bucket" "upload" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_ownership_controls" "owner" {
  bucket = aws_s3_bucket.upload.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "private" {
  depends_on = [aws_s3_bucket_ownership_controls.owner]

  bucket = aws_s3_bucket.upload.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket                  = aws_s3_bucket.upload.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.upload.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = false
  }
}

data "aws_iam_policy_document" "secure_transport" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.upload.arn,
      "${aws_s3_bucket.upload.arn}/*"
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
    condition {
      test     = "NumericLessThan"
      variable = "s3:TlsVersion"
      values   = ["1.2"]
    }
  }
}

resource "aws_s3_bucket_policy" "secure_transport" {
  bucket = aws_s3_bucket.upload.id
  policy = data.aws_iam_policy_document.secure_transport.json
}

resource "aws_s3_object" "root_disk" {
  bucket = aws_s3_bucket.upload.id
  key    = local.root_disk_object_key
  source = var.root_disk_path

  lifecycle {
    replace_triggered_by = [terraform_data.root_disk_hash]
  }
}

resource "aws_s3_object" "test_disk" {
  bucket = aws_s3_bucket.upload.id
  key    = local.test_disk_object_key
  source = var.test_disk_path

  lifecycle {
    replace_triggered_by = [terraform_data.test_disk_hash]
  }
}

resource "aws_ebs_snapshot_import" "root_disk" {
  disk_container {
    format = "RAW"
    user_bucket {
      s3_bucket = aws_s3_bucket.upload.bucket
      s3_key    = aws_s3_object.root_disk.key
    }
  }

  lifecycle {
    replace_triggered_by = [terraform_data.root_disk_hash]
  }
}

resource "aws_ebs_snapshot_import" "test_disk" {
  disk_container {
    format = "RAW"
    user_bucket {
      s3_bucket = aws_s3_bucket.upload.bucket
      s3_key    = aws_s3_object.test_disk.key
    }
  }

  lifecycle {
    replace_triggered_by = [terraform_data.test_disk_hash]
  }
}

resource "aws_ami" "image" {
  name                = local.ami_name
  virtualization_type = "hvm"
  ena_support         = true
  architecture        = var.image_requirements.arch
  boot_mode           = local.boot_mode

  root_device_name = "/dev/xvda"

  ebs_block_device {
    device_name           = "/dev/xvda"
    snapshot_id           = aws_ebs_snapshot_import.root_disk.id
    volume_type           = "gp3"
    delete_on_termination = true
  }
}
