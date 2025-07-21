
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
    # "terraform-aws-modules/apigateway-v2/aws" = {
    #   source  = "terraform-aws-modules/apigateway-v2/aws"
    #   version = "~> 4.0"
    # }
    # "terraform-aws-modules/s3-bucket/aws" = {
    #   source  = "terraform-aws-modules/s3-bucket/aws"
    #   version = "~> 4.0"
    # }
    # "terraform-aws-modules/lambda/aws" = {
    #   source  = "terraform-aws-modules/lambda/aws"
    #   version = "~> 7.0"
    # }
  }
}