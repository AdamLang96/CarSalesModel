output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_arn" {
  description = "RDS database ARN"
  value       = aws_db_instance.main.arn
}

output "flask_server_ecr_url" {
  description = "Flask server ECR repository URL"
  value       = aws_ecr_repository.flask_server.repository_url
}

output "webscraper_ecr_url" {
  description = "Webscraper ECR repository URL"
  value       = aws_ecr_repository.webscraper.repository_url
}

output "model_training_ecr_url" {
  description = "Model training ECR repository URL"
  value       = aws_ecr_repository.model_training.repository_url
}

output "streamlit_ecr_url" {
  description = "Streamlit ECR repository URL"
  value       = aws_ecr_repository.streamlit.repository_url
}

output "models_s3_bucket" {
  description = "S3 bucket name for ML models"
  value       = aws_s3_bucket.models.id
}

output "shap_explainers_s3_bucket" {
  description = "S3 bucket name for SHAP explainers"
  value       = aws_s3_bucket.shap_explainers.id
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}