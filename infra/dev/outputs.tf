output "files_thumbnails_bucket_name" {
  value = module.files_thumbnails_bucket.bucket_name
}

output "document_processing_queue_name" {
  value = module.document_processing_queue.queue_name
}

output "document_processing_dead_letter_queue_name" {
  value = module.document_processing_dead_letter_queue.queue_name
}

output "knowledge_base_id" {
  value = module.s3_vector_kb.knowledge_base_id
}

output "knowledge_base_data_source_id" {
  value = module.s3_vector_kb.knowledge_base_data_source_id
}