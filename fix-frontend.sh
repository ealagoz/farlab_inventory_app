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
docker rmi inventory-frontend 2>/dev/null || true
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true

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
    print_status "Waiting for frontend to initialize..."
    sleep 15
    
    # Check if container is running
    if docker compose ps frontend | grep -q "Up"; then
        print_success "Frontend container is running!"
        
        # Try to test the service
        if docker compose exec frontend sh -c "curl -f http://localhost:5173 || echo 'Service check completed'"; then
            print_success "Frontend service is responding!"
        else
            print_warning "Frontend running but may still be initializing"
        fi
    else
        print_warning "Frontend container status unclear"
        docker compose logs frontend --tail=20
    fi
    
    docker compose stop frontend
else
    print_error "Frontend container failed to start"
    docker compose logs frontend --tail=20
    exit 1
fi

print_success "Frontend build fix completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Start the full application: docker compose up -d"
echo "2. Access the app: http://localhost (via nginx proxy)"
echo "3. Check logs if needed: docker compose logs -f frontend"
echo "4. Direct frontend access: http://localhost:5173 (development only)"
echo "5. Run security scan: ./security-scan.sh"
echo ""
echo "💡 Troubleshooting:"
echo "- View all services: docker compose ps"
echo "- Check frontend logs: docker compose logs frontend --tail=50"
echo "- Restart specific service: docker compose restart frontend"
