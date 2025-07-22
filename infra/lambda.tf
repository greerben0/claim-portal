module "lambda_function_create_claim" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  publish       = true
  function_name = "${local.name}-create-claim"
  handler       = "create_claim.lambda_handler"
  runtime       = "python3.13"

  source_path = [
    "../backend/create_claim",
    "../backend/auth_check",
  ]

  tags = local.tags

  environment_variables = {
    FILE_S3_BUCKET_NAME      = module.claims_bucket.s3_bucket_id
    FILE_METADATA_TABLE_NAME = module.claims_table.dynamodb_table_id
  }

  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = "${module.claims_bucket.s3_bucket_arn}/*"
      },
      {
        Action   = "logs:*"
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action   = "dynamodb:PutItem"
        Effect   = "Allow"
        Resource = module.claims_table.dynamodb_table_arn
      }
    ]
  })
  attach_policy_json = true

  allowed_triggers = {
    APIGateway = {
      service    = "apigateway"
      source_arn = "${aws_apigatewayv2_api.claim_portal.execution_arn}/*/*"
    },
  }

  vpc_subnet_ids                     = module.vpc.intra_subnets
  vpc_security_group_ids             = [module.security_group_lambda.security_group_id]
  attach_network_policy              = true
  replace_security_groups_on_destroy = true
  replacement_security_group_ids     = [module.vpc.default_security_group_id]
}

module "lambda_function_get_claims" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  publish       = true
  function_name = "${local.name}-get-claims"
  handler       = "get_claims.lambda_handler"
  runtime       = "python3.13"

  source_path = [
    "../backend/get_claims",
    "../backend/auth_check",
  ]

  tags = local.tags

  environment_variables = {
    FILE_METADATA_TABLE_NAME = module.claims_table.dynamodb_table_id
  }

  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "logs:*"
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:ListItems",
          "dynamodb:Query",
        ]
        Effect   = "Allow"
        Resource = module.claims_table.dynamodb_table_arn
      }
    ]
  })
  attach_policy_json = true

  allowed_triggers = {
    APIGateway = {
      service    = "apigateway"
      source_arn = "${aws_apigatewayv2_api.claim_portal.execution_arn}/*/*"
    },
  }

  vpc_subnet_ids                     = module.vpc.intra_subnets
  vpc_security_group_ids             = [module.security_group_lambda.security_group_id]
  attach_network_policy              = true
  replace_security_groups_on_destroy = true
  replacement_security_group_ids     = [module.vpc.default_security_group_id]
}