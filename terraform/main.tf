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

resource "aws_lambda_function" "this" {
  function_name = var.lambda_function_name
  handler       = var.lambda_handler_name
  role          = aws_iam_role.iam_for_lambda.arn

  source_code_hash = filebase64sha256("../service.py")
  runtime          = "python3.8"

  environment {
    variables = {
      foo = "bar"
    }
  }
}

resource "aws_lambda_event_source_mapping" "this" {
  event_source_arn = "${aws_sqs_queue.request_notification_queue.arn}"
  function_name    = "${aws_lambda_function.this.arn}"
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "sqs.ReceiveMessage",
        "sqs.DeleteMessage",
        "sqs.GetQueueAttributes"
      ],
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
