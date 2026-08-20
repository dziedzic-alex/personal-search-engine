module "files_thumbnails_bucket" {
  source        = "../modules/s3-bucket"
  bucket_name   = "pse-${var.environment}-files-thumbs"
  environment   = var.environment
  force_destroy = true
}

module "supplemental_data_storage_bucket" {
  source = "../modules/s3-bucket"
  bucket_name = "pse-${var.environment}-supplemental-data-storage-kb"
  environment = var.environment
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

module "s3_vector_kb" {
  source = "../modules/s3-vector-kb"
  region = "us-east-1"
  source_s3_bucket_arn = module.files_thumbnails_bucket.bucket_arn
  supplemental_data_storage_s3_bucket_name = module.supplemental_data_storage_bucket.bucket_name
  supplemental_data_storage_s3_bucket_arn = module.supplemental_data_storage_bucket.bucket_arn
  vector_bucket_name = "pse-${var.environment}-s3-vector-kb"
  vector_bucket_index_name = "pse-${var.environment}-s3-vector-kb-index"
  embedding_model_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-2-multimodal-embeddings-v1:0"
  embedding_dimensions = 1024
  embedding_similarity_metric = "cosine"
  knowledge_base_name = "pse-${var.environment}-document-kb"
  kb_data_source_name = "pse-${var.environment}-document-kb-data-source"
  knowledge_base_iam_role_name = "pse-${var.environment}-document-kb-role"
  knowledge_base_iam_role_policy_name = "pse-${var.environment}-document-kb-policy"
  parsing_strategy = "BEDROCK_FOUNDATION_MODEL"
  bedrock_foundation_model_configuration = {
    model_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0"
  }
  chunking_strategy = "SEMANTIC"
  semantic_chunking_configuration = {
    breakpoint_percentile_threshold = 95
    buffer_size = 1
    max_token = 300
  }
  enable_cloudwatch_logs = true
}