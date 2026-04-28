resource "aws_ecr_repository" "flask_server" {
  name                 = "${var.project_name}-flask-server"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-flask-server"
  }
}

resource "aws_ecr_repository" "webscraper" {
  name                 = "${var.project_name}-webscraper"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-webscraper"
  }
}

resource "aws_ecr_repository" "model_training" {
  name                 = "${var.project_name}-model-training"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-model-training"
  }
}

resource "aws_ecr_repository" "streamlit" {
  name                 = "${var.project_name}-streamlit"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-streamlit"
  }
}

resource "aws_ecr_repository" "react_frontend" {
  name                 = "${var.project_name}-react-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-react-frontend"
  }
}