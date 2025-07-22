output "cloudfront_endpoint" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "webapp_deploy_command" {
  value = "aws s3 cp --recursive frontend/dist/ s3://${aws_s3_bucket.frontend.id}/"
}