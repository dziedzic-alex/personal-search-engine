output "queue_name" {
  value = aws_sqs_queue.this.name
}

output "queue_arn" {
  value = aws_sqs_queue.this.arn
}