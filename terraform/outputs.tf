output "notification_queue_arn" {
  value = aws_sqs_queue.request_notification_queue.arn
}

output "notification_queue_url" {
  value = aws_sqs_queue.request_notification_queue.id
}
