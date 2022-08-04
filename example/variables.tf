variable "aws_instance_type" {
  default = "t2.nano"
}

variable "region" {
  default = "us-east-1"
}

variable "vpc_name" {
  type = string
}

variable "subnet_name" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {
    Name: "dynamic-tagging"
  }
}
