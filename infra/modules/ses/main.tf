data "aws_region" "current" {}

resource "aws_ses_domain_identity" "this" {
  domain = var.domain
  region = coalesce(var.region, data.aws_region.current.region)
}

resource "aws_ses_domain_dkim" "this" {
  domain = aws_ses_domain_identity.this.domain
}

resource "aws_route53_record" "dkim" {
  count   = 3
  zone_id = var.zone_id
  name    = "${aws_ses_domain_dkim.this.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = 600
  records = ["${aws_ses_domain_dkim.this.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_route53_record" "dmarc" {
  zone_id = var.zone_id
  name    = "_dmarc.${aws_ses_domain_identity.this.domain}"
  type    = "TXT"
  ttl     = 600
  records = ["v=DMARC1; p=none;"]
}