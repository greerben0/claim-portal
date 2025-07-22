resource "aws_apigatewayv2_api" "claim_portal" {
  name          = "claim-portal-${local.name}"
  protocol_type = "HTTP"
  description   = "API Gateway for the Claim Portal"

  cors_configuration {
    allow_origins = local.allowed_origins
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
  }
}

resource "aws_apigatewayv2_stage" "claim_portal" {
  api_id = aws_apigatewayv2_api.claim_portal.id

  name        = "claim-portal-${local.name}"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "create_claim" {
  api_id = aws_apigatewayv2_api.claim_portal.id

  integration_uri        = module.lambda_function_create_claim.lambda_function_invoke_arn
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "get_claims" {
  api_id = aws_apigatewayv2_api.claim_portal.id

  integration_uri        = module.lambda_function_get_claims.lambda_function_invoke_arn
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_claims" {
  api_id             = aws_apigatewayv2_api.claim_portal.id
  route_key          = "GET /claim"
  target             = "integrations/${aws_apigatewayv2_integration.get_claims.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt_authorizer.id
}

resource "aws_apigatewayv2_route" "create_claim" {
  api_id = aws_apigatewayv2_api.claim_portal.id

  route_key          = "POST /claim"
  target             = "integrations/${aws_apigatewayv2_integration.create_claim.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt_authorizer.id
}


resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.claim_portal.name}"

  retention_in_days = 30
}

resource "aws_apigatewayv2_deployment" "claim_portal" {
  api_id      = aws_apigatewayv2_api.claim_portal.id
  description = "deployment"

  lifecycle {
    create_before_destroy = true
  }
  depends_on = [aws_apigatewayv2_route.get_claims, aws_apigatewayv2_route.create_claim]
}

resource "aws_apigatewayv2_authorizer" "jwt_authorizer" {
  api_id           = aws_apigatewayv2_api.claim_portal.id
  authorizer_type  = "JWT"
  name             = "jwt_authorizer"
  identity_sources = ["$request.header.Authorization"]
  jwt_configuration {
    audience = [aws_cognito_user_pool_client.client.id]
    issuer   = "https://${aws_cognito_user_pool.pool.endpoint}"
  }
}