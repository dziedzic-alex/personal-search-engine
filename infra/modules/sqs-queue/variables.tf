variable "name" {
  type        = string
  description = "The name of the SQS queue"
}

variable "region" {
  type        = string
  description = "The AWS region to create the SQS queue in"
  default     = null
  nullable    = true
}

variable "max_message_size" {
  type        = number
  description = "The maximum message size in bytes"
  default     = 262144 # 256 KB
}

variable "delay_seconds" {
  type        = number
  description = "Time in seconds that the delivery of all messages in the queue will be delayed"
  default     = 0
}

variable "visibility_timeout_seconds" {
  type        = number
  description = "The visibility timeout in seconds for the SQS queue"
  default     = 30
}

variable "message_retention_seconds" {
  type        = number
  description = "The number of seconds to keep a message in the queue"
  default     = 345600 # 4 days
}

variable "receive_wait_time_seconds" {
  type        = number
  description = "The time for which a ReceiveMessage call will wait for a message to arrive(long polling) before returning"
  default     = 0
}

variable "sqs_managed_sse_enabled" {
  type        = bool
  description = "Whether to enable SQS managed server-side encryption"
  default     = true
}

variable "policy" {
  type        = string
  description = "The policy for the SQS queue"
  default     = null
  nullable    = true
}

variable "redrive_policy" {
  type        = string
  description = "The redrive policy for the SQS queue"
  default     = null
  nullable    = true
}

variable "redrive_allow_policy" {
  type        = string
  description = "The redrive allow policy for the SQS queue"
  default     = null
  nullable    = true
}

variable "environment" {
  type        = string
  description = "The environment for the SQS queue"
}