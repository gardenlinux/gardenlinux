locals {
  test_name            = var.test_name
  test_name_safe       = replace(local.test_name, "_", "-")
  test_name_safe_short = substr(local.test_name_safe, 0, 24)
  feature_tpm2         = contains(var.features, "_tpm2")
  feature_trustedboot  = contains(var.features, "_trustedboot")
  uefi_required        = contains(var.features, "_usi")
  boot_mode            = local.uefi_required ? "uefi" : "legacy-bios"
  arch                 = var.arch == "amd64" ? "x86_64" : var.arch
  # https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
  # max 63 chars
  bucket_name          = substr("images-${local.test_name_safe}", 0, 63)
  tar_name             = "image-${local.test_name}.tar.gz"
  image_name           = "image-${local.test_name}"
  net_name             = "net-${local.test_name}"
  subnet_name          = "subnet-${local.test_name}"
  instance_name        = "instance-${local.test_name}"
  fw_name              = "fw-${local.test_name}"
  igw_name             = "igw-${local.test_name}"
  route_table_name     = "rt-${local.test_name}"
  disk_os_name         = "disk-os-${local.test_name}"
  ssh_key_name         = "ssh-${var.ssh_user}-${local.test_name}"
  ssh_private_key_file = split(".pub", var.ssh_public_key)[0]
  ssh_parameters       = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"
  public_ip            = aws_instance.instance.public_ip
  labels = {
    component = "gardenlinux"
    test-type = "platform-test"
    test-name = local.test_name
  }
  labels_sec_ebs_enc = {
    # sec-by-def-ebs-encryption-exception = "enabled"
  }
  labels_name = {
    Name = local.test_name
  }

  image_source_type = split("://", var.image_path)[0]
  image = (
    local.image_source_type == "file" ? "${split("file://", var.image_path)[1]}/${var.image_file}" :
    local.image_source_type == "cloud" ? var.image_file :
    null
  )
}

resource "aws_s3_bucket" "images" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = local.bucket_name

  tags = merge(
    local.labels,
    { Name = local.bucket_name }
  )
}

resource "aws_s3_bucket_ownership_controls" "images_owner" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = aws_s3_bucket.images.0.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "images_acl" {
  count = local.image_source_type == "file" ? 1 : 0

  depends_on = [aws_s3_bucket_ownership_controls.images_owner.0]

  bucket = aws_s3_bucket.images.0.id
  acl    = "private"
}

data "aws_iam_policy_document" "policy_document" {
  count = local.image_source_type == "file" ? 1 : 0

  statement {
    # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document#principals-and-not_principals
    # principal = "*"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    effect = "Deny"
    actions = [
      "s3:*"
    ]
    resources = [
      aws_s3_bucket.images.0.arn,
      "${aws_s3_bucket.images.0.arn}/*"
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

resource "aws_s3_bucket_policy" "images_policy" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = aws_s3_bucket.images.0.id
  policy = data.aws_iam_policy_document.policy_document.0.json
}

resource "aws_s3_bucket_public_access_block" "no_public_access" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = aws_s3_bucket.images.0.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "images_encryption" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = aws_s3_bucket.images.0.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = false
  }
}

# data "aws_vpc" "default" {
#   default = true
# }

resource "aws_vpc" "net" {
  cidr_block           = var.net_range
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    local.labels,
    { Name = local.net_name }
  )
}

resource "aws_subnet" "subnet" {
  cidr_block = var.subnet_range
  vpc_id     = aws_vpc.net.id
  # availability_zone = var.availability_zone

  tags = merge(
    local.labels,
    { Name = local.subnet_name }
  )
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.net.id

  tags = merge(
    local.labels,
    { Name = local.igw_name }
  )
}

resource "aws_route_table" "igw" {
  vpc_id = aws_vpc.net.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = merge(
    local.labels,
    { Name = local.route_table_name }
  )
}

resource "aws_route_table_association" "igw_vm" {
  route_table_id = aws_route_table.igw.id
  subnet_id      = aws_subnet.subnet.id
}

resource "aws_security_group" "sg" {
  name = local.fw_name

  # vpc_id = data.aws_vpc.default.id
  vpc_id = aws_vpc.net.id

  ingress {
    cidr_blocks = [
      # "0.0.0.0/0"
      "${var.my_ip}/32"
    ]
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    local.labels,
    { Name = local.fw_name }
  )
}

resource "aws_s3_object" "image" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = aws_s3_bucket.images.0.id
  key    = local.image_name

  tags = merge(
    local.labels,
    { Name = local.image_name }
  )
}

resource "aws_ebs_snapshot_import" "snapshot_import" {
  count = local.image_source_type == "file" ? 1 : 0

  disk_container {
    # format = "VHD"
    format = "RAW"
    user_bucket {
      s3_bucket = aws_s3_bucket.images.0.bucket
      s3_key    = aws_s3_object.image.0.key
    }
  }

  # forces replacement
  # description = "uploaded by gardenlinux-cicd"

  tags = merge(
    local.labels,
    { Name = local.image_name }
  )
}

resource "aws_ami" "ami" {
  count = local.image_source_type == "file" ? 1 : 0

  name                = local.image_name
  description         = "gardenlinux"
  ena_support         = true
  virtualization_type = "hvm"
  architecture        = local.arch
  # TODO: check if we need to set this
  # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ami-boot.html
  boot_mode        = local.boot_mode
  root_device_name = "/dev/xvda"
  ebs_block_device {
    device_name = "/dev/xvda"
    snapshot_id = aws_ebs_snapshot_import.snapshot_import.0.id
  }

  tpm_support = local.feature_trustedboot ? "v2.0" : null
  uefi_data   = local.feature_trustedboot ? file("cert/secureboot.aws-efivars") : null

  tags = merge(
    local.labels,
    { Name = local.image_name }
  )
}

resource "aws_key_pair" "ssh_key" {
  key_name   = local.ssh_key_name
  public_key = file(var.ssh_public_key)

  tags = merge(
    local.labels,
    { Name = local.ssh_key_name }
  )
}

resource "aws_instance" "instance" {
  ami = (
    local.image_source_type == "file" ? aws_ami.ami.0.id :
    local.image_source_type == "cloud" ? var.image_file :
    null
  )
  instance_type = var.instance_type
  subnet_id     = aws_subnet.subnet.id

  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.sg.id]

  user_data = file("vm-startup-script.sh")
  key_name  = aws_key_pair.ssh_key.key_name

  root_block_device {
    delete_on_termination = true
    volume_type           = "gp3"
    volume_size           = 16
    encrypted             = false

    tags = merge(
      local.labels,
      { Name = local.disk_os_name }
    )
  }

  depends_on = [aws_internet_gateway.igw]

  tags = merge(
    local.labels,
    { Name = local.instance_name }
  )
}

resource "null_resource" "test_connect" {
  depends_on = [aws_instance.instance]

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
