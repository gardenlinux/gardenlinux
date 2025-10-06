resource "aws_vpc" "net" {
  cidr_block           = var.provider_vars.net_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    local.labels,
    { Name = local.net_name }
  )

}

resource "aws_subnet" "subnet" {
  vpc_id     = aws_vpc.net.id
  cidr_block = var.provider_vars.subnet_cidr

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

resource "aws_security_group" "default" {
  name   = local.fw_name
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

  tags = merge(
    local.labels,
    { Name = local.fw_name }
  )
}
