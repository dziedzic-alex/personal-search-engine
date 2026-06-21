data "aws_region" "current" {}

resource "aws_s3_bucket" "this" {
    bucket_prefix = var.bucket_prefix
    bucket_namespace = "account-regional"
    region = coalesce(var.region, data.aws_region.current.region)
    force_destroy = var.force_destroy

    tags = {
        Environment = var.environment
    }
}

resource "aws_s3_bucket_policy" "this" {
    count = var.policy != null ? 1 : 0
    bucket = aws_s3_bucket.this.bucket
    policy = var.policy
}