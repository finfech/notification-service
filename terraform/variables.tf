variable "lambda_function_name" {
  default = "notification-service"
}

variable "lambda_handler_name" {
  default = "service.handler"
}

variable "lambda_filename" {
  default = "service.zip"
}

variable "ses_aws_region" {
  type = string
}

variable "ses_sender_email" {
  type = string
}