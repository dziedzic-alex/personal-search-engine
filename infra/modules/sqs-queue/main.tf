data "aws_region" "current" {}

resource "aws_sqs_queue" "this" {
    name = var.name
    region = coalesce(var.region, data.aws_region.current.region)
    max_message_size = var.max_message_size
    delay_seconds = var.delay_seconds
    visibility_timeout_seconds = var.visibility_timeout_seconds
    message_retention_seconds = var.message_retention_seconds
    receive_wait_time_seconds = var.receive_wait_time_seconds
    sqs_managed_sse_enabled = var.sqs_managed_sse_enabled

    tags = {
        Environment = var.environment
    }
}

resource "aws_sqs_queue_policy" "this" {
    count = var.policy != null ? 1 : 0
    queue_url = aws_sqs_queue.this.id
    policy = var.policy
    region = coalesce(var.region, data.aws_region.current.region)
}

resource "aws_sqs_queue_redrive_policy" "this" {
    count = var.redrive_policy != null ? 1 : 0
    queue_url = aws_sqs_queue.this.id
    redrive_policy = var.redrive_policy
    region = coalesce(var.region, data.aws_region.current.region)
}

resource "aws_sqs_queue_redrive_allow_policy" "this" {
    count = var.redrive_allow_policy != null ? 1 : 0
    queue_url = aws_sqs_queue.this.id
    redrive_allow_policy = var.redrive_allow_policy
    region = coalesce(var.region, data.aws_region.current.region)
}