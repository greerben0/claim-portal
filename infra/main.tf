provider "aws" {
  region = var.aws_region
}


resource "random_string" "uuid" {
  length  = 8
  special = false
  lower   = true
}

locals {
  name         = "claim-portal-${lower(random_string.uuid.result)}"
  region       = var.aws_region
  jwt_audience = local.name

  tags = {
    Project = local.name
  }

  s3_origin_id = "${local.name}S3Origin"
}


module "claims_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${local.name}-claims"
  acl    = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  versioning = {
    enabled = true
  }
}

module "claims_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name         = "${local.name}-claims"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "user_id"
  range_key = "created_at"

  attributes = [
    { name = "user_id", type = "S" },
    { name = "created_at", type = "S" }, # ISO 8601 format UTC timezone
  ]
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = local.tags
}