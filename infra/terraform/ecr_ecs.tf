resource "aws_ecr_repository" "movies_rag" {
  name                 = "movies-rag"
  image_scanning_configuration { scan_on_push = true }
  image_tag_mutability        = "MUTABLE"
}

resource "aws_ecs_cluster" "movies" {
  name = "movies-rag-cluster"
}

data "aws_iam_policy_document" "ecs_task_assume_role_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "movies" {
  family                   = "movies-rag-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "movies-rag-app"
      image = "${aws_ecr_repository.movies_rag.repository_url}:latest"
      portMappings = [
        { containerPort = 8000, hostPort = 8000, protocol = "tcp" }
      ]
      environment = [
        { name = "DATABASE_URL",    value = "postgres://${var.db_username}:${var.db_password}@${aws_db_instance.movies.address}:5432/${var.db_name}" },
        { name = "OPENAI_API_KEY",   value = var.openai_api_key },
        { name = "MOVIES_CSV_PATH",  value = "/app/movies-dataset.csv" }
      ]
    }
  ])
}
