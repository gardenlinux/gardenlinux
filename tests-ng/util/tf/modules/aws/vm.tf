resource "aws_key_pair" "ssh" {
  key_name   = local.ssh_key_name
  public_key = file(var.ssh_public_key_path)

  tags = merge(
    local.labels,
    { Name = local.ssh_key_name }
  )
}

resource "aws_instance" "vm" {
  ami           = var.existing_root_disk != "" ? var.existing_root_disk : aws_ami.image[0].id
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

  ebs_block_device {
    device_name = "/dev/xvdb"
    snapshot_id = aws_ebs_snapshot_import.test_disk.id
  }

  tags = merge(
    local.labels,
    { Name = local.test_name }
  )

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash,
      terraform_data.test_disk_hash,
    ]
  }
}

output "vm_ip" {
  value       = aws_instance.vm.public_ip
  description = "Public IPv4 of the VM"
}

output "ssh_user" {
  value       = var.provider_vars.ssh_user
}

output "image_requirements" {
  value       = var.image_requirements
  description = "Image requirements"
}
