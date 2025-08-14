resource "aws_vpc" "net" {
  cidr_block           = var.provider_vars.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

}

resource "aws_subnet" "subnet" {
  vpc_id     = aws_vpc.net.id
  cidr_block = var.provider_vars.public_subnet_cidr
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.net.id
}

resource "aws_route_table" "igw" {
  vpc_id = aws_vpc.net.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "igw_vm" {
  route_table_id = aws_route_table.igw.id
  subnet_id      = aws_subnet.subnet.id
}

resource "aws_security_group" "default" {
  name   = local.sg_name
  vpc_id = aws_vpc.net.id

  ingress {
    cidr_blocks = [
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
}

resource "aws_key_pair" "ssh" {
  key_name   = local.key_name
  public_key = file(var.ssh_public_key_path)
}

resource "aws_instance" "vm" {
  ami           = aws_ami.image.id
  instance_type = local.instance_type

  subnet_id                   = aws_subnet.subnet.id
  vpc_security_group_ids      = [aws_security_group.default.id]
  associate_public_ip_address = true

  key_name  = aws_key_pair.ssh.key_name
  user_data = file(var.user_data_script_path)

  depends_on = [aws_internet_gateway.igw]

  root_block_device {
    delete_on_termination = true
    volume_type           = "gp3"
    volume_size           = 16
    encrypted             = false
  }

  dynamic "ebs_block_device" {
    for_each = var.use_scp ? [] : [1]
    content {
      device_name = "/dev/xvdb"
      snapshot_id = aws_ebs_snapshot_import.test_disk[0].id
    }
  }
}

output "vm_ip" {
  value       = aws_instance.vm.public_ip
  description = "Public IPv4 of the VM"
}
