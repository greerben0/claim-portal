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
  deployed_callback_urls = [
    "https://${aws_cloudfront_distribution.s3_distribution.domain_name}"
  ]

  local_callback_urls = [
    "http://localhost:5173"
  ]

  callback_urls = var.local ? concat(local.deployed_callback_urls, local.local_callback_urls) : local.deployed_callback_urls

  logout_urls = local.callback_urls

  s3_origin_id = "${local.name}S3Origin"

  deployed_origins = [
    "https://${aws_cloudfront_distribution.s3_distribution.domain_name}",
    "https://${aws_s3_bucket.frontend.bucket_regional_domain_name}",
  ]

  allowed_origins = var.local ? concat(local.deployed_origins, ["http://localhost:5173"]) : local.deployed_origins

  vite_env_content = templatefile("${path.module}/env.tftpl", {
    user_pool_region    = local.region,
    user_pool_name      = aws_cognito_user_pool.pool.name
    user_pool_id        = aws_cognito_user_pool.pool.id
    user_pool_client_id = aws_cognito_user_pool_client.client.id
    backend_domain      = aws_apigatewayv2_stage.claim_portal.invoke_url
  })
}


module "claims_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"
  version = "5.2.0"

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
  version = "5.0.0"


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

resource "local_file" "vite_env_file" {
  content  = local.vite_env_content
  filename = "${path.module}/../frontend/.env"
}