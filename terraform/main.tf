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
    # Environment variables for credentials
    # OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME, OS_USER_DOMAIN_NAME
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
    default = "m1.large" # 4 vCPU, 16 GB RAM ===> check this!
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

data "openstack_images_image_v2" "ubuntu" {
  name = var.image_name
  most_recent = true
}

data "openstack_compute_flavor_v2" "flavor" {
  name = var.flavor_name  
}

data "openstack_networking_network_v2" "network" {
  name = "dualStack" # or your network name in NREC
}

# --- Data Resources ---
# Security Group & Rules
resource "openstack_networking_secgroup_v2" "inventory_sg" {
    name = "inventory-app-sg"
    description = "Security group for inventory application"
}
resource "openstack_networking_secgroup_rule_v2" "ssh" {
    direction = "ingress"
    ethertype = "IPv4"
    protocol = "tcp"
    port_range_min = 22
    port_range_max = 22
    remote_ip_prefix = "0.0.0.0/0"
    security_group_id = openstack_networking_secgroup_v2.inventory_sg.id
}
resource "openstack_networking_secgroup_rule_v2" "http" {
    direction = "ingress"
    ethertype = "IPv4"
    protocol = "tcp"
    port_range_min = 80
    port_range_max = 80
    remote_ip_prefix = "0.0.0.0/0"
    security_group_id = openstack_networking_secgroup_v2.inventory_sg.id
}
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
    public_key = file("~/.ssh/${var.key_pair_name}.pub")
}
# Volume for PostgreSQL Data
resource "openstack_blockstorage_volume_v3" "postgres_data" {
    name = "postgres-data-volume"
    description = "Persistent volume for Inventory App PostgreSQL data"
    size = 10 # Size in GB ===> Check this
    availability_zone = var.region 
}
# Compute Instance
resource "openstack_compute_instance_v2" "inventory_server" {
    name = "inventory-production-server"
    image_id = data.openstack_images_image_v2.ubuntu.id
    flavor_id = data.openstack_compute_flavor_v2.flavor.id
    key_pair = openstack_compute_keypair_v2.inventory_key.name
    security_groups = [openstack_networking_secgroup_v2.inventory_sg.name]
    availability_zone = var.region

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

        # Secrets
        postgres_password = var.postgres_password
        admin_password = var.admin_password
        secret_key = var.secret_key
    }))
}

# Volume Attachment
resource "openstack_compute_volume_attach_v2" "postgres_attach" {
    instance_id = openstack_compute_instance_v2.inventory_server.id
    volume_id = openstack_blockstorage_volume_v3.postgres_data.id
    device = "/dev/vdb" # Check this ====>
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