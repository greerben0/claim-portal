variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "local" {
  description = "Set true for working with local webapp development"
  type        = bool
  default     = false
}