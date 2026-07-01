module "files_thumbnails_bucket" {
  source        = "../modules/s3-bucket"
  bucket_name   = "pse-${var.environment}-files-thumbs"
  environment   = var.environment
  force_destroy = true
}

module "document_processing_queue" {
  source                     = "../modules/sqs-queue"
  name                       = "pse-${var.environment}-document-processing"
  environment                = var.environment
  max_message_size           = 2048
  visibility_timeout_seconds = 180
  receive_wait_time_seconds  = 2
  redrive_policy = jsonencode({
    deadLetterTargetArn = module.document_processing_dead_letter_queue.queue_arn
    maxReceiveCount     = 3
  })
}

module "document_processing_dead_letter_queue" {
  source                    = "../modules/sqs-queue"
  name                      = "pse-${var.environment}-document-processing-dead-letter"
  environment               = var.environment
  max_message_size          = 2048
  message_retention_seconds = 1209600 # 14 days
  receive_wait_time_seconds = 3
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [module.document_processing_queue.queue_arn]
  })
}