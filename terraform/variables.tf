variable "aws_region" {
  default = "ap-northeast-2"
}


variable "lambda_function_name" {
  default = "notification-service"
}

variable "lambda_handler_name" {
  default = "app.handler"
}

variable "lambda_filename" {
  default = "app.zip"
}

variable "lambda_source_path" {
  default = "../app.py"
}

variable "ses_aws_region" {
  type = string
}

variable "ses_sender_email" {
  type = string
}

variable "commit_hash" {
  default = "test"
}
