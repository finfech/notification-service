provider "aws" {}

terraform {
  backend "remote" {
    organization = "vapias"
    workspaces {
      name = "notification-service"
    }
  }
}

resource "aws_sqs_queue" "request_notification_queue" {
  name                        = "request-notification-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
}
