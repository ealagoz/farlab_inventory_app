# terraform/main.tf - NREC Optimized & Updated for Git Deployment

terraform {
    required_version = ">= 1.0"
    required_providers {
        openstack = {
            source = "terraform-provider-openstack/openstack"
            version = "~> 1.54.0"
        }
    }
}

# NREC OpenStack Provider 
provider "openstack" {
    auth_url = "https://api.nrec.no:5000"
    region = var.region
}

# --- Variables ---
variable "region" {
    description = "NREC region (bgo or osl)"
    type = string
    default = "bgo"
}
variable "key_pair_name" {
    description = "SSH key pair name for the instance"
    type = string
}
variable "flavor_name" {
    description = "NREC instance flavor"
    type = string
    default = "m1.xlarge" # 4 vCPU, 16 GB RAM ===> check this!
}
variable "image_name" {
    description = "NREC instance image"
    type = string
    default = "GOLD Ubuntu 24.04 LTS"
}

# Application Configuration Variables
variable "git_repo_url" {
    description = "URL of the git repository containing the application code"
    type = string
}
variable "db_user" {
    description = "PostgreSQL username"
    type = string
}
variable "db_name" {
    description = "PostgreSQL database name"
    type = string
}
variable "admin_name" {
    description = "Default admin username"
    type = string
}
variable "admin_email" {
    description = "Default admin email"
    type = string
    sensitive = true 
}
# Sensitive Variables for Secrets
variable "postgres_password" {
    description = "Password for the PostgreSQL user"
    type = string
    sensitive = true
}
variable "admin_password" {
    description = "Password for the default admin user"
    type = string
    sensitive = true
}
variable "secret_key" {
    description = "JWT Secret Key for the application"
    type = string
    sensitive = true
}

# Flavor image size
variable "root_disk_size" {
  description = "Size of the main data volume in GB"
  type        = number
  default     = 150
}
# variable "data_volume_size" {
#     description = "Size of the separate data volume in GB"
#     type = number
#     default = 50
# }

# Allowed IP ranges
variable "allowed_ssh_ips" {
    description = "List of IP ranges allowed to SSH"
    type = list(string)
    default = ["129.241.0.0/16"]
}

data "openstack_images_image_v2" "ubuntu" {
  name = var.image_name
  most_recent = true
}

data "openstack_compute_flavor_v2" "flavor" {
  name = var.flavor_name  
}

data "openstack_networking_network_v2" "network" {
  name = "dualStack" # NREC standard dual-stack network
}

# --- Data Resources ---
# Security Group & Rules - NREC Compliant (without outgoing egress rules)
resource "openstack_networking_secgroup_v2" "inventory_sg" {
    name = "inventory-app-sg"
    description = "Security group for inventory application"

    tags = [
        "environment:production",
        "application:inventory", 
        "owner:farlab",
        "project:uib-farlab-inventory"
    ]
}

# SSH rules - IPv4
resource "openstack_networking_secgroup_rule_v2" "ssh" {
    count = length(var.allowed_ssh_ips)
    direction = "ingress"
    ethertype = "IPv4"
    protocol = "tcp"
    port_range_min = 22
    port_range_max = 22
    remote_ip_prefix = var.allowed_ssh_ips[count.index]
    security_group_id = openstack_networking_secgroup_v2.inventory_sg.id
}

# HTTP rules - IPv4
resource "openstack_networking_secgroup_rule_v2" "http" {
    direction = "ingress"
    ethertype = "IPv4"
    protocol = "tcp"
    port_range_min = 80
    port_range_max = 80
    remote_ip_prefix = "0.0.0.0/0"
    security_group_id = openstack_networking_secgroup_v2.inventory_sg.id
}

# HTTPS rules - IPv4
resource "openstack_networking_secgroup_rule_v2" "https" {
    direction = "ingress"
    ethertype = "IPv4"
    protocol = "tcp"
    port_range_min = 443
    port_range_max = 443
    remote_ip_prefix = "0.0.0.0/0"
    security_group_id = openstack_networking_secgroup_v2.inventory_sg.id
}

# SSH Key Pair
resource "openstack_compute_keypair_v2" "inventory_key" {
    name = var.key_pair_name
    public_key = file("/Users/jaz/.ssh/${var.key_pair_name}.pub")
}

# The Main Compute Instance
resource "openstack_compute_instance_v2" "inventory_server" {
    name = "inventory-production-server"
    flavor_id = data.openstack_compute_flavor_v2.flavor.id
    key_pair = openstack_compute_keypair_v2.inventory_key.name
    security_groups = [
        # openstack_networking_secgroup_v2.inventory_sg.id,
        openstack_networking_secgroup_v2.inventory_sg.name,
        "default" # Keep default for inter-instance communication
        ]

    # Block Device 1: The Root/Boot Disk
    block_device {
        uuid                  = data.openstack_images_image_v2.ubuntu.id
        source_type           = "image"
        destination_type      = "volume"
        volume_size           = var.root_disk_size
        boot_index            = 0
        delete_on_termination = true
    }

    # Project tags
    metadata = {
        Environment = "production"
        Application = "inventory"
        Owner = "farlab"
        Project = "uib-farlab-inventory"
    }

    network {
        name = data.openstack_networking_network_v2.network.name
    }

    # Pass all variables to the cloud-init template
    user_data = base64encode(templatefile("${path.module}/cloud-init.yml", {
        # App config
        git_repo_url = var.git_repo_url
        db_user = var.db_user
        db_name = var.db_name
        admin_name = var.admin_name
        admin_email = var.admin_email
        # SSH key for appuser
        ssh_public_key = openstack_compute_keypair_v2.inventory_key.public_key
        # Secrets
        postgres_password = var.postgres_password
        admin_password = var.admin_password
        secret_key = var.secret_key
    }))

    # Ensure instance is created after all security group rules
    depends_on = [
        openstack_networking_secgroup_rule_v2.ssh,
        openstack_networking_secgroup_rule_v2.http,
        openstack_networking_secgroup_rule_v2.https
    ]
}

# --- Outpts ---
output "instance_ip" {
    description = "Public IP address of the server"
    value = openstack_compute_instance_v2.inventory_server.access_ip_v4
}
output "ssh_command" {
    description = "Command to SSH into the server"
    value = "ssh -i ~/.ssh/${var.key_pair_name} ubuntu@${openstack_compute_instance_v2.inventory_server.access_ip_v4}"
}
# Output for SSH debugging
output "ssh_debug_info" {
    description = "SSH connection information for debugging"
    value = {
        instance_ip = openstack_compute_instance_v2.inventory_server.access_ip_v4
        instance_ipv6 = openstack_compute_instance_v2.inventory_server.access_ip_v6
        # Use 'appuser' since that's what cloud-init creates, or keep 'ubuntu' as default
        ssh_command_ipv4 = "ssh -i ~/.ssh/${var.key_pair_name} appuser@${openstack_compute_instance_v2.inventory_server.access_ip_v4}"
        ssh_command_ipv6 = "ssh -i ~/.ssh/${var.key_pair_name} appuser@[${openstack_compute_instance_v2.inventory_server.access_ip_v6}]"
        default_user = "ubuntu"
        app_user = "appuser"
        note = "Default user is 'ubuntu', but cloud-init creates 'appuser'. Use 'appuser' for application access."
    }
}