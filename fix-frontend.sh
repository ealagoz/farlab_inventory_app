#!/bin/bash

set -e

echo "🔧 Fixing ARM64 frontend build issues..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Stop any running containers
print_status "Stopping running containers..."
docker compose down || true

# Remove problematic images
print_status "Removing existing frontend image..."
docker rmi inventory-frontend:latest 2>/dev/null || true

# Clean up any build cache
print_status "Cleaning Docker build cache..."
docker builder prune -f

# Remove problematic node_modules from host if mounted
print_status "Cleaning local node_modules if exists..."
rm -rf ./farlab-inventory-frontend/node_modules 2>/dev/null || true
rm -rf ./farlab-inventory-frontend/package-lock.json 2>/dev/null || true

# Check system architecture
print_status "System architecture: $(uname -m)"

# Build with no cache to ensure fresh build
print_status "Rebuilding frontend image (this may take a few minutes)..."
docker compose build --no-cache frontend

print_success "Frontend image rebuilt successfully!"

# Test the build
print_status "Testing frontend container startup..."
if docker compose up -d frontend; then
    sleep 10
    if docker compose exec frontend wget --no-verbose --tries=1 --spider http://localhost:5173; then
        print_success "Frontend container is running correctly!"
    else
        print_warning "Frontend container started but health check failed"
    fi
    docker compose stop frontend
else
    print_error "Frontend container failed to start"
    exit 1
fi

print_success "Frontend build fix completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Start the full application: docker compose up -d"
echo "2. Check logs if needed: docker compose logs frontend"
echo "3. Run security scan: ./security-scan.sh"
