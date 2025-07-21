
# output "cognito_login_url" {
#   value = "https://${aws_cognito_user_pool.pool.domain}.auth.${local.region}.amazoncognito.com/login?client_id=${aws_cognito_user_pool_client.client.id}&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost/callback"
# }

# output "cognito_client_id" {
#   value = aws_cognito_user_pool_client.client.id
# }

# output "cognito_authorization_endpoint" {
#   value = "https://${aws_cognito_user_pool.pool.domain}.auth.${local.region}.amazoncognito.com/oauth2/authorize"
# }

# output "cognito_token_endpoint" {
#   value = "https://${aws_cognito_user_pool.pool.domain}.auth.${local.region}.amazoncognito.com/oauth2/token"
# }

# output "api_upload_endpoint" {
#   value = "${aws_apigatewayv2_api.claim_portal.api_endpoint}/upload"
# }


output "cloudfront_endpoint" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "webapp_deploy_command" {
  value = "aws s3 cp --recursive frontend/dist/ s3://${aws_s3_bucket.frontend.id}/"
}