output "alb_dns_name" {
  description = "URL del Application Load Balancer"
  value       = aws_lb.alb.dns_name
}

output "db_endpoint" {
  description = "Endpoint de la base de datos PostgreSQL"
  value       = aws_db_instance.movies.address
}
