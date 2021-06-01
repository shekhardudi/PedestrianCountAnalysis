terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "ap-southeast-2"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "step-count-data-bucket-sh"
  acl    = "private"

  tags = {
    Name        = "data bucket"
  }
}
resource "aws_s3_bucket" "output_bucket" {
  bucket = "step-count-output-bucket-sh"
  acl    = "private"

  tags = {
    Name        = "output bucket"
  }
}

resource "aws_s3_bucket" "script_bucket" {
  bucket = "step-script-bucket-sh"
  acl    = "private"

  tags = {
    Name        = "output bucket"
  }
}

resource "aws_iam_role" "access_for_glue" {
  name = "AccessRoleForGlueSH"

  assume_role_policy = jsonencode( # whitespace changes
            {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "glue.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
        )
}

resource "aws_iam_role_policy_attachment" "attach_glue_service_role" {
    role       = "${aws_iam_role.access_for_glue.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
    depends_on = [
        aws_iam_role.access_for_glue
  ]
}

resource "aws_iam_role_policy_attachment" "attach_s3_access" {
    role       = "${aws_iam_role.access_for_glue.name}"
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    depends_on = [
        aws_iam_role.access_for_glue
  ]
}

resource "aws_iam_role_policy_attachment" "attach_rds_access" {
    role       = "${aws_iam_role.access_for_glue.name}"
    policy_arn = "arn:aws:iam::aws:policy/AmazonRDSDataFullAccess"
    depends_on = [
        aws_iam_role.access_for_glue
    ]
}


module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name                 = "rds-sh"
  cidr                 = "10.0.0.0/16"
  azs                  = ["ap-southeast-2a","ap-southeast-2b"]
  public_subnets       = ["10.0.4.0/24","10.0.5.0/24"]
  enable_dns_hostnames = true
  enable_dns_support   = true
}


resource "aws_db_subnet_group" "rds-sh" {
  name       = "rds-sh"
  subnet_ids = module.vpc.public_subnets

  tags = {
    Name = "rds-sh"
  }
}

resource "aws_security_group" "rds" {
  name        = "rds"
  description = "Allow TCP inbound traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description      = "Port"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "All"
    from_port        = 0
    to_port          = 65535
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "allow_port"
  
  }
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.ap-southeast-2.s3"
}

resource "aws_vpc_endpoint_route_table_association" "private_s3" {
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
  route_table_id  = module.vpc.public_route_table_ids[0]
  
}

resource "aws_db_instance" "rds-sh" {
  identifier             = "rds-sh"
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  engine                 = "postgres"
  engine_version         = "13.1"
  username               = "postgresuser"
  password               = "secret99"
  name                   = "MyDB"
  db_subnet_group_name   = aws_db_subnet_group.rds-sh.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.rds-sh.name
  publicly_accessible    = true
  skip_final_snapshot    = true
  iam_database_authentication_enabled = true
}


resource "aws_db_parameter_group" "rds-sh" {
  name   = "rds-sh"
  family = "postgres13"

  parameter {
    name  = "log_connections"
    value = "1"
  }
}

resource "aws_glue_catalog_database" "aws_glue_catalog_database" {
  name = "step-count-analysis-sh"
}

resource "aws_glue_crawler" "stepper-crawler-sh" {
  database_name = aws_glue_catalog_database.aws_glue_catalog_database.name
  name          = "stepper-crawler-sh"
  role          = aws_iam_role.access_for_glue.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_bucket.bucket}"
  }
}

resource "aws_glue_connection" "PostGresConSh" {
  connection_properties = {
    JDBC_CONNECTION_URL = "jdbc:postgresql://${aws_db_instance.rds-sh.endpoint}/MyDB"
    PASSWORD            = aws_db_instance.rds-sh.password
    USERNAME            =  aws_db_instance.rds-sh.username
  }

  name = "PostGresConSh"

  physical_connection_requirements {
    availability_zone      = module.vpc.azs[0]
    security_group_id_list = [aws_security_group.rds.id]
    subnet_id              = module.vpc.public_subnets[0]
  }
}

resource "aws_glue_job" "count-steps-job-sh" {
  glue_version = "2.0"
  name         = "count-steps-job-sh"
  description  = "count-steps-job monthly daily"
  role_arn     = aws_iam_role.access_for_glue.arn
  max_capacity = 1
  max_retries  = 1
  connections  = [aws_glue_connection.PostGresConSh.name]
  timeout      = 5

  command {
    script_location = "s3://${aws_s3_bucket.script_bucket.bucket}/GlueJob.py"
  }



  execution_property {
    max_concurrent_runs = 1
  }
}