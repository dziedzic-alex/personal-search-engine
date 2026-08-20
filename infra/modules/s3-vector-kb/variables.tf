variable "source_s3_bucket_arn" {
    type = string
    description = "The arn of the s3 bucket with the source documents"
}

variable "supplemental_data_storage_s3_bucket_name" {
    type = string
    description = "The name of the supplemental data storage bucket. Needed when using a multimodal embedding model that directly embeds images."
    default = null
    nullable = true
}

variable "supplemental_data_storage_s3_bucket_arn" {
    type = string
    description = "The arn of the supplemental data storage bucket. Needed when using a multimodal embedding model that directly embeds images."
    default = null
    nullable = true

    validation {
        condition = (
            (var.supplemental_data_storage_s3_bucket_name != null && var.supplemental_data_storage_s3_bucket_arn != null) ||
            (var.supplemental_data_storage_s3_bucket_name == null && var.supplemental_data_storage_s3_bucket_arn == null)
        )
        error_message = "supplemental_data_storage_s3_bucket_name and supplemental_data_storage_s3_bucket_arn must be either both set or both null."
    }  
}

variable "vector_bucket_name" {
    type = string
    description = "The name of the vector bucket"
}

variable "vector_bucket_index_name" {
    type = string
    description = "The name of the s3 vector bucket index"
}

variable "embedding_dimensions" {
    type = number
    description = "The number of dimensions per embedding. Make sure the chosen embedding model supports the chosen number of dimensions"
}

variable "knowledge_base_name" {
    type = string
    description = "The name of the knowledge base"
}

variable "region" {
  type        = string
  description = "The region to create knowledge base resources in"
  default     = null
  nullable    = true
}

variable "embedding_similarity_metric" {
    type = string
    description = "The similarity metric to use for the embedding"
    default = "cosine"

    validation {
        condition = contains(["euclidean", "cosine"], var.embedding_similarity_metric)
        error_message = "The embedding similarity metric must be either euclidean or cosine"
    }
}

variable "kb_data_source_name" {
    type = string
    description = "The name of the knowledge base data source resource"
}


variable "embedding_model_arn" {
    type = string
    description = "The arn of the embedding model to use"
}

variable "knowledge_base_iam_role_name" {
    type = string
    description = "The name of the iam role to use for the knowledge base"
}

variable "knowledge_base_iam_role_policy_name" {
    type = string
    description = "The name of the iam role policy to use for the knowledge base"
}

variable "parsing_strategy" {
  type        = string
  description = "The strategy to use for parsing"

  validation {
    condition     = contains(["BEDROCK_FOUNDATION_MODEL", "BEDROCK_DATA_AUTOMATION"], var.parsing_strategy)
    error_message = "The parsing strategy must be either BEDROCK_FOUNDATION_MODEL or BEDROCK_DATA_AUTOMATION"
  }
}

variable "bedrock_foundation_model_configuration" {
    type = object({
      model_arn = string
      parsing_prompt = optional(string)
    })
    description = "Required when parsing_strategy is BEDROCK_FOUNDATION_MODEL"
    default     = null
    nullable    = true

    validation {
      condition = (
        (var.parsing_strategy == "BEDROCK_FOUNDATION_MODEL" && var.bedrock_foundation_model_configuration != null) ||
        (var.parsing_strategy != "BEDROCK_FOUNDATION_MODEL" && var.bedrock_foundation_model_configuration == null)
      )
      error_message = "bedrock_foundation_model_configuration must be set only when parsing_strategy is BEDROCK_FOUNDATION_MODEL."
    }
}

variable "chunking_strategy" {
  type        = string
  description = "How to chunk source documents for the knowledge base data source"

  validation {
    condition     = contains(["FIXED_SIZE", "HIERARCHICAL", "SEMANTIC"], var.chunking_strategy)
    error_message = "chunking_strategy must be FIXED_SIZE, HIERARCHICAL, or SEMANTIC."
  }
}

variable "fixed_size_chunking_configuration" {
  type = object({
    max_tokens         = number
    overlap_percentage = optional(number)
  })
  description = "Required when chunking_strategy is FIXED_SIZE"
  default     = null
  nullable    = true

  validation {
    condition = (
      (var.chunking_strategy == "FIXED_SIZE" && var.fixed_size_chunking_configuration != null) ||
      (var.chunking_strategy != "FIXED_SIZE" && var.fixed_size_chunking_configuration == null)
    )
    error_message = "fixed_size_chunking_configuration must be set only when chunking_strategy is FIXED_SIZE."
  }
}

variable "hierarchical_chunking_configuration" {
  type = object({
    overlap_tokens = number
    level_configurations = list(object({
      max_tokens = number
    }))
  })
  description = "Required when chunking_strategy is HIERARCHICAL. level_configurations must contain exactly two levels."
  default     = null
  nullable    = true

  validation {
    condition = (
      (var.chunking_strategy == "HIERARCHICAL" && var.hierarchical_chunking_configuration != null) ||
      (var.chunking_strategy != "HIERARCHICAL" && var.hierarchical_chunking_configuration == null)
    )
    error_message = "hierarchical_chunking_configuration must be set only when chunking_strategy is HIERARCHICAL."
  }

  validation {
    condition = (
      var.hierarchical_chunking_configuration == null ||
      length(var.hierarchical_chunking_configuration.level_configurations) == 2
    )
    error_message = "hierarchical_chunking_configuration.level_configurations must contain exactly two levels."
  }
}

variable "semantic_chunking_configuration" {
  type = object({
    breakpoint_percentile_threshold = number
    buffer_size                     = number
    max_token                       = number
  })
  description = "Required when chunking_strategy is SEMANTIC"
  default     = null
  nullable    = true

  validation {
    condition = (
      (var.chunking_strategy == "SEMANTIC" && var.semantic_chunking_configuration != null) ||
      (var.chunking_strategy != "SEMANTIC" && var.semantic_chunking_configuration == null)
    )
    error_message = "semantic_chunking_configuration must be set only when chunking_strategy is SEMANTIC."
  }
}

variable "enable_cloudwatch_logs" {
  type        = bool
  description = "Whether to enable cloudwatch logs for the knowledge base"
  default     = false
}