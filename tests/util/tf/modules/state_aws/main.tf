variable "test_name" {
  description = "Resources will include this name string for reference"
}

variable "test_environment" {
  description = "Resources will include this environment string for reference"
}

module "terraform_state_backend" {
  source  = "cloudposse/tfstate-backend/aws"
  version = "1.5.0"

  force_destroy    = true
  bucket_enabled   = true
  dynamodb_enabled = false
  name             = var.test_name
  environment      = var.test_environment
  namespace        = "gardenlinux"
}

output "bucket_name" {
  value = module.terraform_state_backend.s3_bucket_id
}
