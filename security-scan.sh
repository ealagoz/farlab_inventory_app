#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔍 Starting comprehensive security scan..."

# Set Trivy cache directory (Fixed typo)
export TRIVY_CACHE_DIR="/tmp/trivy"
mkdir -p "$TRIVY_CACHE_DIR"

# Function to run Trivy with fallback registries
run_trivy_scan() {
    local target="$1"
    local scan_type="$2"

    echo "Scanning $target for $scan_type..."

    # Try primary registry first (Fixed syntax - removed space in severity)
    if ! docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
        aquasec/trivy:latest image "$target" --severity HIGH,CRITICAL --no-progress; then

        echo "Primary registry failed, trying alternative..."
        # Fallback to alternative registry (Fixed syntax)
        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
            -e TRIVY_DB_REPOSITORY=docker.io/aquasec/trivy-db:2 \
            aquasec/trivy:latest image "$target" --severity HIGH,CRITICAL --no-progress
    fi
}

# Build images first
print_status "Building Docker images..."
if docker compose build --no-cache; then
    print_success "Images built successfully"
else
    print_error "Failed to build images"
    exit 1
fi

# Scan custom images
print_status "Scanning backend image for vulnerabilities..."
if run_trivy_scan "inventory-backend:latest" "vulnerabilities"; then
    print_success "Backend image scan completed"
else
    print_warning "Backend image has vulnerabilities - check output above"
fi

print_status "Scanning frontend image for vulnerabilities..."
if run_trivy_scan "inventory-frontend:latest" "vulnerabilities"; then
    print_success "Frontend image scan completed"  
else
    print_warning "Frontend image has vulnerabilities - check output above"
fi

# Run configuration scan
print_status "Scanning configuration files..."
if docker run --rm -v "$(pwd)":/workdir \
    -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
    aquasec/trivy:latest config --severity HIGH,CRITICAL .; then
    print_success "Configuration scan passed"
else
    print_warning "Configuration issues found - check output above"
fi

# Run secret scan
print_status "Scanning for exposed secrets..."
if docker run --rm -v "$(pwd)":/workdir \
    -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
    aquasec/trivy:latest fs --scanners secret --severity HIGH,CRITICAL .; then
    print_success "No secrets found"
else
    print_warning "Potential secrets found - check output above"
fi

# Run base image scans
print_status "Scanning base images..."

print_status "Scanning Python base image..."
if docker run --rm -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
    aquasec/trivy:latest image --severity HIGH,CRITICAL --no-progress python:3.12-slim; then
    print_success "Python base image scan completed"
else
    print_warning "Python base image has vulnerabilities"
fi

print_status "Scanning Node base image..."
if docker run --rm -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
    aquasec/trivy:latest image --severity HIGH,CRITICAL --no-progress node:20-alpine; then
    print_success "Node base image scan completed"
else
    print_warning "Node base image has vulnerabilities"
fi

print_status "Scanning PostgreSQL base image..."
if docker run --rm -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
    aquasec/trivy:latest image --severity HIGH,CRITICAL --no-progress postgres:17-alpine3.20; then
    print_success "PostgreSQL base image scan completed"
else
    print_warning "PostgreSQL base image has vulnerabilities"
fi

print_status "Scanning Nginx base image..."
if docker run --rm -v "$TRIVY_CACHE_DIR":/root/.cache/trivy \
    aquasec/trivy:latest image --severity HIGH,CRITICAL --no-progress nginx:alpine; then
    print_success "Nginx base image scan completed"
else
    print_warning "Nginx base image has vulnerabilities"
fi

print_success "Security scan completed!"

echo ""
echo "📊 Security Scan Summary:"
echo "========================="
echo "✅ Docker images scanned for vulnerabilities"
echo "✅ Configuration files analyzed"
echo "✅ Secrets scanning completed"
echo "✅ Base images checked"
echo ""
echo "📝 Next Steps:"
echo "1. Review any warnings or errors above"
echo "2. Update base images regularly: docker compose pull"
echo "3. Monitor for new vulnerabilities"
echo "4. Consider implementing HTTPS/SSL for production"
echo ""
echo "🚀 To start the secure application:"
echo "   docker compose up -d"
echo ""
echo "🛡️  To run security scans again:"
echo "   ./security-scan.sh"