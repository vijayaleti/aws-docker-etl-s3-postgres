variable "project_name" {
  type        = string
  description = "Prefix for S3 bucket and IAM user"
  default     = "light-etl-demo"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

