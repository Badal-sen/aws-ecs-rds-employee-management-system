resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/employee-app"
  retention_in_days = 7
}