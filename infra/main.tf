resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.project_name}-raw"

  tags = {
    Name        = "${var.project_name}-raw"
    Environment = "dev"
  }
}
resource "aws_s3_bucket" "processed_data" {
  bucket = "${var.project_name}-processed"

  tags = {
    Name        = "${var.project_name}-processed"
    Environment = "dev"
  }
}

resource "aws_iam_user" "etl_user" {
  name = "${var.project_name}-etl-user"
  path = "/system/"
}

resource "aws_iam_access_key" "etl_user_key" {
  user = aws_iam_user.etl_user.name
}
data "aws_iam_policy_document" "etl_s3_policy" {
  statement {
    sid    = "AllowListBuckets"
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.raw_data.arn,
      aws_s3_bucket.processed_data.arn
    ]
  }

  statement {
    sid    = "AllowObjectRW"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${aws_s3_bucket.raw_data.arn}/*",
      "${aws_s3_bucket.processed_data.arn}/*"
    ]
  }
}

resource "aws_iam_user_policy" "etl_s3_policy" {
  name   = "${var.project_name}-etl-s3"
  user   = aws_iam_user.etl_user.name
  policy = data.aws_iam_policy_document.etl_s3_policy.json
}


