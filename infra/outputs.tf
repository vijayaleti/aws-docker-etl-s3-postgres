output "etl_access_key_id" {
  description = "Access key for ETL user"
  value       = aws_iam_access_key.etl_user_key.id
  sensitive   = true
}

output "etl_secret_access_key" {
  description = "Secret key for ETL user"
  value       = aws_iam_access_key.etl_user_key.secret
  sensitive   = true
}

output "raw_bucket_name" {
  description = "Raw S3 bucket name"
  value       = aws_s3_bucket.raw_data.bucket
}

output "processed_bucket_name" {
  description = "Processed S3 bucket name"
  value       = aws_s3_bucket.processed_data.bucket
}


