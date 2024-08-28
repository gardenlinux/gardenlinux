data "external" "my_ip" {
  program = ["curl", "-q", "https://api.ipify.org?format=json"]
}

provider "aws" {
  region  = var.region
}

locals {
  my_ip = data.external.my_ip.result.ip
  uuid = uuid()
  bucket_name   = "images-${var.test_name}-upload"
  tar_name      = "image-${var.test_name}.tar.gz"
  image_name    = "image-${var.test_name}"
  # net_name      = "net-${var.test_name}"
  # subnet_name   = "subnet-${var.test_name}"
  # sa_name       = "sa-${var.test_name}"
  instance_name = "instance-${var.test_name}"
  fw_name = "fw-${var.test_name}"
  ssh_private_key_file = split(".pub", var.ssh_public_key)[0]
  ssh_parameters = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"
  public_ip = aws_instance.instance.public_ip
  labels = {
    component =  "gardenlinux"
    test-type =  "platform-test"
    test-name =  var.test_name
    test-uuid =  local.uuid
  }
  labels_sec_ebs_enc = {
    # sec-by-def-ebs-encryption-exception = "enabled"
  }
  labels_name = {
    Name = var.test_name
  }
}

resource "aws_s3_bucket" "images" {
  bucket        = local.bucket_name

  tags = local.labels
}

resource "aws_s3_bucket_ownership_controls" "images_owner" {
  bucket = aws_s3_bucket.images.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "images_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.images_owner]

  bucket = aws_s3_bucket.images.id
  acl    = "private"
}

data "aws_iam_policy_document" "policy_document" {
    statement {
      # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document#principals-and-not_principals
      # principal = "*"
      principals {
        type = "*"
        identifiers = ["*"]
      }
      effect = "Deny"
      actions = [
        "s3:*"
      ]
      resources = [
        aws_s3_bucket.images.arn,
        "${aws_s3_bucket.images.arn}/*"
      ]
      condition {
        test = "Bool"
        variable = "aws:SecureTransport"
        values = ["false"]
      }
      condition {
        test = "NumericLessThan"
        variable = "s3:TlsVersion"
        values = ["1.2"]
      }
    }
}

resource "aws_s3_bucket_policy" "images_policy" {
  bucket = aws_s3_bucket.images.id
  policy = data.aws_iam_policy_document.policy_document.json
}

resource "aws_s3_bucket_public_access_block" "no_public_access" {
  bucket = aws_s3_bucket.images.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "images_encryption" {
  bucket = aws_s3_bucket.images.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
    bucket_key_enabled = false
  }
}

data "aws_vpc" "default" {
  default = true
}

# resource "aws_vpc" "vpc" {
#   cidr_block           = var.cidr_block
#   enable_dns_hostnames = true
#   enable_dns_support   = true
#   tags{
#     Name = "test_env_vpc"
#   }
# }
# 
# resource "aws_subnet" "subnet" {
#   cidr_block        = cidrsubnet(aws_vpc.test_env.cidr_block, 3, 1)
#   vpc_id            = aws_vpc.test_env.id
#   availability_zone = var.availability_zone
# }

# resource "aws_internet_gateway" "igw" {
#   vpc_id = aws_vpc.vpc.id
# }

resource "aws_security_group" "sg" {
  name = local.fw_name

  vpc_id = data.aws_vpc.default.id

  ingress {
    cidr_blocks = [
      # "0.0.0.0/0"
      "${local.my_ip}/32"
    ]
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
  }

  # egress {
  #   from_port   = 0
  #   to_port     = 0
  #   protocol    = -1
  #   cidr_blocks = ["0.0.0.0/0"]
  # }
}

resource "aws_s3_object" "image" {
  bucket = aws_s3_bucket.images.id
  key    = local.image_name
  source = var.image_source

  # The filemd5() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
  # etag = "${md5(file("path/to/file"))}"
  # etag = filemd5(var.image_source)
}

resource "aws_ebs_snapshot_import" "snapshot_import" {
  disk_container {
    # format = "VHD"
    format = "RAW"
    user_bucket {
      s3_bucket = aws_s3_bucket.images.bucket
      s3_key    = aws_s3_object.image.key
    }
  }

  # forces replacement
  # description = "uploaded by gardenlinux-cicd"

  # tags = merge(local.labels, local.labels_snapshot)
  tags = local.labels
}

resource "aws_ami" "ami" {
  name                = local.image_name
  description = "gardenlinux"
  ena_support         = true
  virtualization_type = "hvm"
  architecture = "x86_64"
  boot_mode =  "legacy-bios"
  root_device_name    = "/dev/xvda"
  ebs_block_device {
    device_name = "/dev/xvda"
    snapshot_id = aws_ebs_snapshot_import.snapshot_import.id
  }

  tags = local.labels
}

resource "aws_key_pair" "ssh_key" {
  key_name   = var.test_name
  public_key = file(var.ssh_public_key)
}

resource "aws_instance" "instance" {
  ami           = aws_ami.ami.id
  instance_type = var.instance_type

  
  associate_public_ip_address = true
  security_groups             = [aws_security_group.sg.name]

  user_data = "systemctl start ssh"
  key_name  = aws_key_pair.ssh_key.key_name

  root_block_device {
    delete_on_termination = true
    volume_type           = "gp3"
    volume_size           = 7
    encrypted             = false

    tags = local.labels
  }

  tags = merge(local.labels_name, local.labels)
}

# resource "null_resource" "test_connect" {
#   connection {
#     type     = "ssh"
#     user     = var.ssh_user
#     private_key = file(split(".pub", var.ssh_public_key)[0])
#     host     = aws_instance.instance.public_ip
#   }
# 
#   provisioner "remote-exec" {
#     inline = [
#       "sudo uname -a"
#     ]
#   }
# }

resource "null_resource" "test_connect" {
  provisioner "local-exec" {
    command = "ssh ${local.ssh_parameters} ${aws_instance.instance.public_ip} uname -a"
  }
}
