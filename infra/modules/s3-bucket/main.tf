data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "this" {
  bucket = format(
    "%s-%s-%s-an",
    var.bucket_name,
    data.aws_caller_identity.current.account_id,
    data.aws_region.current.region
  )
  bucket_namespace = "account-regional"
  region           = coalesce(var.region, data.aws_region.current.region)
  force_destroy    = var.force_destroy

  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_policy" "this" {
  count  = var.policy != null ? 1 : 0
  bucket = aws_s3_bucket.this.bucket
  policy = var.policy
}