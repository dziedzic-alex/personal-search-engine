data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_s3vectors_vector_bucket" "this" {
  vector_bucket_name = var.vector_bucket_name
  region             = coalesce(var.region, data.aws_region.current.region)
}

resource "aws_s3vectors_index" "this" {
  index_name         = var.vector_bucket_index_name
  vector_bucket_name = aws_s3vectors_vector_bucket.this.vector_bucket_name
  region             = coalesce(var.region, data.aws_region.current.region)

  data_type       = "float32"
  dimension       = var.embedding_dimensions
  distance_metric = var.embedding_similarity_metric

  metadata_configuration {
    non_filterable_metadata_keys = ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
  }
}

resource "aws_iam_role" "this" {
  name = var.knowledge_base_iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "this" {
  name = var.knowledge_base_iam_role_policy_name
  role = aws_iam_role.this.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      # Source S3 bucket — Get documents for ingestion
      {
        Sid      = "SourceBucketGet"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${var.source_s3_bucket_arn}/*"
        Condition = {
          StringEquals = { "aws:ResourceAccount" = data.aws_caller_identity.current.account_id }
        }
      },
      # S3Vectors — access to the index
      {
        Sid    = "S3VectorsAccess"
        Effect = "Allow"
        Action = [
          "s3vectors:GetIndex",
          "s3vectors:QueryVectors",
          "s3vectors:PutVectors",
          "s3vectors:GetVectors",
          "s3vectors:DeleteVectors"
        ]
        Resource = aws_s3vectors_index.this.index_arn
        Condition = {
          StringEquals = { "aws:ResourceAccount" = data.aws_caller_identity.current.account_id }
        }
      },
      # Bedrock — invoke embedding model
      {
        Sid      = "BedrockInvokeModel"
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = var.embedding_model_arn
      }],
      # Supplemental storage bucket — read/write extracted images
      var.supplemental_data_storage_s3_bucket_arn != null ? [
        {
          Sid    = "SupplementalBucket"
          Effect = "Allow"
          Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject"
          ]
          Resource = "${var.supplemental_data_storage_s3_bucket_arn}/*"

          Condition = {
            StringEquals = { "aws:ResourceAccount" = data.aws_caller_identity.current.account_id }
          }
        },
        {
          Sid      = "SupplementalBucketList"
          Effect   = "Allow"
          Action   = ["s3:ListBucket"]
          Resource = var.supplemental_data_storage_s3_bucket_arn
          Condition = {
            StringEquals = { "aws:ResourceAccount" = data.aws_caller_identity.current.account_id }
          }
        }
      ] : [],
      # Bedrock foundation model - invoke parsing model
      var.parsing_strategy == "BEDROCK_FOUNDATION_MODEL" ? [
        {
          Sid      = "BedrockFoundationModelInvoke"
          Effect   = "Allow"
          Action   = ["bedrock:InvokeModel"]
          Resource = var.bedrock_foundation_model_configuration.model_arn
        }
      ] : []
    )
  })
}

resource "aws_bedrockagent_knowledge_base" "this" {
  depends_on = [aws_iam_role_policy.this]

  name     = var.knowledge_base_name
  role_arn = aws_iam_role.this.arn
  region   = coalesce(var.region, data.aws_region.current.region)

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = var.embedding_model_arn

      embedding_model_configuration {
        bedrock_embedding_model_configuration {
          dimensions          = var.embedding_dimensions
          embedding_data_type = "FLOAT32"
        }
      }

      dynamic "supplemental_data_storage_configuration" {
        for_each = var.supplemental_data_storage_s3_bucket_name != null ? [1] : []

        content {
          storage_location {
            type = "S3"
            s3_location {
              uri = "s3://${var.supplemental_data_storage_s3_bucket_name}"
            }
          }
        }
      }
    }
  }

  storage_configuration {
    type = "S3_VECTORS"
    s3_vectors_configuration {
      index_arn = aws_s3vectors_index.this.index_arn
    }
  }
}

resource "aws_bedrockagent_data_source" "this" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.this.id
  name              = var.kb_data_source_name
  region            = coalesce(var.region, data.aws_region.current.region)

  data_source_configuration {
    type = "CUSTOM"
  }

  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = var.chunking_strategy

      dynamic "fixed_size_chunking_configuration" {
        for_each = var.chunking_strategy == "FIXED_SIZE" ? [var.fixed_size_chunking_configuration] : []

        content {
          max_tokens         = fixed_size_chunking_configuration.value.max_tokens
          overlap_percentage = fixed_size_chunking_configuration.value.overlap_percentage
        }
      }

      dynamic "hierarchical_chunking_configuration" {
        for_each = var.chunking_strategy == "HIERARCHICAL" ? [var.hierarchical_chunking_configuration] : []

        content {
          overlap_tokens = hierarchical_chunking_configuration.value.overlap_tokens

          dynamic "level_configuration" {
            for_each = hierarchical_chunking_configuration.value.level_configurations

            content {
              max_tokens = level_configuration.value.max_tokens
            }
          }
        }
      }

      dynamic "semantic_chunking_configuration" {
        for_each = var.chunking_strategy == "SEMANTIC" ? [var.semantic_chunking_configuration] : []

        content {
          breakpoint_percentile_threshold = semantic_chunking_configuration.value.breakpoint_percentile_threshold
          buffer_size                     = semantic_chunking_configuration.value.buffer_size
          max_token                       = semantic_chunking_configuration.value.max_token
        }
      }
    }

    parsing_configuration {
      parsing_strategy = var.parsing_strategy

      dynamic "bedrock_foundation_model_configuration" {
        for_each = var.parsing_strategy == "BEDROCK_FOUNDATION_MODEL" ? [var.bedrock_foundation_model_configuration] : []

        content {
          model_arn        = bedrock_foundation_model_configuration.value.model_arn
          parsing_modality = "MULTIMODAL"
          dynamic "parsing_prompt" {
            for_each = bedrock_foundation_model_configuration.value.parsing_prompt != null ? [1] : []

            content {
              parsing_prompt_string = bedrock_foundation_model_configuration.value.parsing_prompt
            }
          }
        }
      }

      dynamic "bedrock_data_automation_configuration" {
        for_each = var.parsing_strategy == "BEDROCK_DATA_AUTOMATION" ? [1] : []

        content {
          parsing_modality = "MULTIMODAL"
        }
      }
    }
  }
}

resource "aws_cloudwatch_log_delivery_source" "this" {
  count        = var.enable_cloudwatch_logs ? 1 : 0
  region       = coalesce(var.region, data.aws_region.current.region)
  name         = "bedrock-kb-${aws_bedrockagent_knowledge_base.this.id}"
  log_type     = "APPLICATION_LOGS"
  resource_arn = aws_bedrockagent_knowledge_base.this.arn
}


resource "aws_cloudwatch_log_group" "this" {
  count             = var.enable_cloudwatch_logs ? 1 : 0
  region            = coalesce(var.region, data.aws_region.current.region)
  name              = "/aws/vendedlogs/bedrock/knowledge-base/APPLICATION_LOGS/${aws_bedrockagent_knowledge_base.this.id}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_resource_policy" "this" {
  count       = var.enable_cloudwatch_logs ? 1 : 0
  region      = coalesce(var.region, data.aws_region.current.region)
  policy_name = "bedrock-kb-${aws_bedrockagent_knowledge_base.this.id}-policy"
  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSLogDeliveryWrite"
        Effect = "Allow"
        Principal = {
          Service = ["delivery.logs.amazonaws.com"]
        }
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = ["${aws_cloudwatch_log_group.this[0].arn}:log-stream:*"]
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          },
        }
      }
    ]
  })
}

resource "aws_cloudwatch_log_delivery_destination" "this" {
  count  = var.enable_cloudwatch_logs ? 1 : 0
  region = coalesce(var.region, data.aws_region.current.region)
  name   = "bedrock-kb-${aws_bedrockagent_knowledge_base.this.id}-cloudwatch-logs"
  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.this[0].arn
  }
  depends_on    = [aws_cloudwatch_log_resource_policy.this]
  output_format = "json"
}

resource "aws_cloudwatch_log_delivery" "this" {
  count                    = var.enable_cloudwatch_logs ? 1 : 0
  region                   = coalesce(var.region, data.aws_region.current.region)
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.this[0].arn
  delivery_source_name     = aws_cloudwatch_log_delivery_source.this[0].name
}
