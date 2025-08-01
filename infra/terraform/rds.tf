resource "aws_db_instance" "movies" {
  identifier              = "movies-rag-db"
  allocated_storage       = 20
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = "db.t3.micro"
  name                    = var.db_name
  username                = var.db_username
  password                = var.db_password
  skip_final_snapshot     = true
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  db_subnet_group_name    = aws_db_subnet_group.movies_subnet.id
  publicly_accessible     = false
  apply_immediately       = true
}
