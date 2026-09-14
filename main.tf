provider "aws" {
  region = "us-east-2"
}

resource "aws_iam_role" "lambda_role" {
  name = "internwatch-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "internwatch_scanner" {
  function_name = "internwatch-scanner"
  filename      = "lambda_deployment.zip"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      DB_HOST     = "workout-tracker-db.c928mmeie85x.us-east-2.rds.amazonaws.com"
      DB_PORT     = "5432"
      DB_NAME     = "internwatch_db"
      DB_USER     = "postgres"
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_cloudwatch_event_rule" "internwatch_schedule" {
  name                = "internwatch-schedule"
  schedule_expression = "rate(30 minutes)"
}

resource "aws_cloudwatch_event_target" "internwatch_target" {
  rule      = aws_cloudwatch_event_rule.internwatch_schedule.name
  target_id = "internwatch-scanner"
  arn       = aws_lambda_function.internwatch_scanner.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.internwatch_scanner.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.internwatch_schedule.arn
}