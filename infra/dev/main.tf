module "files_thumbnails_bucket" {
    source = "../modules/s3-bucket"
    bucket_prefix = "personal-search-${var.environment}-files-thumbnails"
    environment = var.environment
    force_destroy = true
}