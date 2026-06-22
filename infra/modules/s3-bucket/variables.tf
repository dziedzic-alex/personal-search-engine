variable "bucket_name" {
  type        = string
  description = "The name for the S3 bucket"
}

variable "region" {
  type        = string
  description = "The region for the S3 bucket"
  default     = null
  nullable    = true
}

variable "force_destroy" {
  type        = bool
  description = "Whether to force destroy the S3 bucket"
  default     = false
}

variable "environment" {
  type        = string
  description = "The environment for the S3 bucket"
}

variable "policy" {
  type        = string
  description = "The policy for the S3 bucket"
  default     = null
  nullable    = true
}