variable "domain" {
    description = "The domain to use for SES email sending"
    type = string
}

variable "region" {
    description = "The region where the SES configuration will be managed"
    type = string
    default = null
    nullable = true
}

variable "zone_id" {
    description = "The Route 53 zone ID to create the DNS records in"
    type = string
}