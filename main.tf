terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}
variable "aws_azs" { default = ["eu-central-1b", "eu-central-1c"] }

provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.aws_region
}

####################################################################################################

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "aa-vpc"
  cidr = "10.0.0.0/16"

  azs            = var.aws_azs
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_nat_gateway = true

  enable_dns_hostnames = true
  enable_dns_support   = true
}

####################################################################################################

variable "db_username" { type = string }
variable "db_password" { type = string }

resource "aws_db_subnet_group" "aa-db-sub-g" {
  name       = "aa-db-sg"
  subnet_ids = module.vpc.public_subnets
}

resource "aws_security_group" "aa-db-sec-g" {
  name   = "aa-db-sec-g"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "aa-db" {
  identifier        = "aa-db"
  engine            = "postgres"
  engine_version    = "13.7"
  allocated_storage = "5"
  instance_class    = "db.t3.micro"

  db_name  = "postgres"
  username = var.db_username
  password = var.db_password

  multi_az               = false
  availability_zone      = var.aws_azs[0]
  db_subnet_group_name   = aws_db_subnet_group.aa-db-sub-g.id
  vpc_security_group_ids = [aws_security_group.aa-db-sec-g.id]
  publicly_accessible    = true
  apply_immediately      = true
  skip_final_snapshot    = true
}

locals {
  sqla_db_url = "postgresql+psycopg2://${var.db_username}:${var.db_password}@${aws_db_instance.aa-db.endpoint}/postgres"
}

####################################################################################################

resource "aws_ecr_repository" "aa-repository" {
  name = "aa-repository"
}

resource "aws_ecr_lifecycle_policy" "aa-repository-lp" {
  repository = aws_ecr_repository.aa-repository.name

  policy = jsonencode({
    rules = [
      {
        rulePriority : 1
        description : "Expire untagged images older than 3 days"
        action = {
          type = "expire"
        }
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 3
        }
      }
    ]
  })
}

resource "aws_ecs_cluster" "aa-cluster" {
  name = "aa-cluster"
}

resource "aws_iam_role" "aa-ecs-exec-role" {
  name = "aa-ecs-exec-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "aa-ecs-policy-attachment" {
  role       = aws_iam_role.aa-ecs-exec-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_security_group" "aa-ecs-sg" {
  name   = "aa-ecs-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_task_definition" "aa-task-definition" {
  family                   = "aa-task-definition"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.aa-ecs-exec-role.arn

  container_definitions = jsonencode([
    {
      name         = "aa-containerm"
      image        = "${aws_ecr_repository.aa-repository.repository_url}:latest"
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      environment = [
        {
          name : "SQLALCHEMY_DATABASE_URL"
          value : local.sqla_db_url
        }
      ]
    }
  ])

}

resource "aws_ecs_service" "aa-service" {
  name            = "aa-service"
  launch_type     = "FARGATE"
  cluster         = aws_ecs_cluster.aa-cluster.id
  task_definition = aws_ecs_task_definition.aa-task-definition.arn
  desired_count   = 1

  network_configuration {
    security_groups  = [aws_security_group.aa-ecs-sg.id]
    subnets          = aws_db_subnet_group.aa-db-sub-g.subnet_ids
    assign_public_ip = true
  }
}

####################################################################################################

output "db_address" {
  value = aws_db_instance.aa-db.address
}


output "db_sqla_url" {
  value = local.sqla_db_url
}

output "ecr_url" {
  value = aws_ecr_repository.aa-repository.repository_url
}
