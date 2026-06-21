terraform {
    required_version = ">= 1.15.6"

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 6.51.0"
        }
    }

    backend "s3" {
        bucket = "personal-search-tf-state-433851229368-us-east-1-an"
        key = "dev/terraform.tfstate"
        region = "us-east-1"
        encrypt = true
    }
}