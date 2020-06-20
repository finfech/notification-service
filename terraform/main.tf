provider "aws" {
  region = var.aws_region
}

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
  filename      = var.lambda_filename
  handler       = var.lambda_handler_name
  role          = aws_iam_role.iam_for_lambda.arn

  source_code_hash = data.archive_file.code.output_base64sha256
  runtime          = "python3.8"

  environment {
    variables = {
      SES_AWS_REGION   = var.ses_aws_region
      SES_SENDER_EMAIL = var.ses_sender_email
    }
  }

  tags = {
    Commit = var.commit_hash
  }
}

resource "aws_lambda_event_source_mapping" "this" {
  event_source_arn = aws_sqs_queue.request_notification_queue.arn
  function_name    = aws_lambda_function.this.arn
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "this" {
  policy_arn = aws_iam_policy.this.arn
  role       = aws_iam_role.iam_for_lambda.name
}

resource "aws_iam_policy" "this" {
  policy = data.aws_iam_policy_document.this.json
}
