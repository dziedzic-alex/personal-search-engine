module "files_thumbnails_bucket" {
  source        = "../modules/s3-bucket"
  bucket_name   = "pse-${var.environment}-files-thumbs"
  environment   = var.environment
  force_destroy = true
}