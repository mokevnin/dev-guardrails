resource "aws_security_group" "example" {
  name = "example"
  description = "Restricted example"
  ingress {
    description = "SSH from private network"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["10.0.0.0/24"]
  }
}
