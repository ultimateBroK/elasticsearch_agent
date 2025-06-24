#!/bin/bash

# ==============================================
# Environment Setup Script
# ==============================================
# This script generates environment files from the master template

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if master template exists
if [ ! -f ".env.template" ]; then
    log_error "Master template .env.template not found!"
    exit 1
fi

log_info "Setting up environment files from master template..."

# Function to generate backend .env
generate_backend_env() {
    log_info "Generating backend/.env.example..."
    
    cat > backend/.env.example << 'EOF'
# ==============================================
# Backend Environment Variables
# ==============================================
# Generated from .env.template - DO NOT EDIT MANUALLY
# Run scripts/setup-env.sh to regenerate

# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_SCHEME=http

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000

# Development
PYTHONUNBUFFERED=1
DEBUG=false

# Cache Settings
QUERY_CACHE_TTL=300
SESSION_TTL=3600

# Agent Settings
MAX_QUERY_SIZE=1000
DEFAULT_CHART_TYPE=bar

# Production overrides (uncomment for production)
# LOG_LEVEL=WARNING
# ELASTICSEARCH_HOST=your-es-host.com
# ELASTICSEARCH_SCHEME=https
# REDIS_HOST=your-redis-host.com
EOF

    log_success "Generated backend/.env.example"
}

# Function to generate frontend .env
generate_frontend_env() {
    log_info "Generating frontend/.env.example..."
    
    cat > frontend/.env.example << 'EOF'
# ==============================================
# Frontend Environment Variables  
# ==============================================
# Generated from .env.template - DO NOT EDIT MANUALLY
# Run scripts/setup-env.sh to regenerate

# API Configuration (NEXT_PUBLIC_ prefix required)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Build Configuration
NODE_ENV=development

# Production overrides (uncomment for production)
# NEXT_PUBLIC_API_URL=https://your-domain.com/api/v1
# NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws
# NODE_ENV=production
EOF

    log_success "Generated frontend/.env.example"
}

# Function to generate root .env.example
generate_root_env() {
    log_info "Generating root .env.example..."
    
    # Simply copy the template to .env.example
    cp .env.template .env.example
    
    log_success "Generated root .env.example"
}

# Function to create actual .env files if they don't exist
create_env_files() {
    log_info "Creating actual .env files (if they don't exist)..."
    
    # Root .env
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_success "Created root .env"
    else
        log_warning "Root .env already exists, skipping"
    fi
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        log_success "Created backend/.env"
    else
        log_warning "Backend .env already exists, skipping"
    fi
    
    # Frontend .env.local
    if [ ! -f "frontend/.env.local" ]; then
        cp frontend/.env.example frontend/.env.local
        log_success "Created frontend/.env.local"
    else
        log_warning "Frontend .env.local already exists, skipping"
    fi
}

# Function to validate environment files
validate_env_files() {
    log_info "Validating environment files..."
    
    local errors=0
    
    # Check if GOOGLE_API_KEY is set in root .env
    if [ -f ".env" ]; then
        if grep -q "GOOGLE_API_KEY=your_gemini_api_key_here" .env; then
            log_warning "Please set your actual GOOGLE_API_KEY in .env"
            ((errors++))
        fi
    fi
    
    # Check if backend .env exists
    if [ ! -f "backend/.env" ]; then
        log_warning "Backend .env file missing"
        ((errors++))
    fi
    
    # Check if frontend .env.local exists
    if [ ! -f "frontend/.env.local" ]; then
        log_warning "Frontend .env.local file missing"
        ((errors++))
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "All environment files are properly configured"
    else
        log_warning "Found $errors configuration issues"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  generate  - Generate all .env.example files from template (default)"
    echo "  create    - Create actual .env files from examples"
    echo "  validate  - Validate existing environment files"
    echo "  clean     - Remove all generated .env files"
    echo "  help      - Show this help message"
}

# Function to clean environment files
clean_env_files() {
    log_info "Cleaning environment files..."
    
    rm -f .env.example backend/.env.example frontend/.env.example
    log_success "Cleaned all .env.example files"
    
    read -p "Do you want to remove actual .env files too? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f .env backend/.env frontend/.env.local
        log_success "Cleaned all .env files"
    fi
}

# Main execution
case "${1:-generate}" in
    "generate")
        generate_root_env
        generate_backend_env
        generate_frontend_env
        log_success "All environment example files generated successfully!"
        echo ""
        log_info "Next steps:"
        echo "  1. Run: $0 create"
        echo "  2. Edit .env with your actual API keys"
        echo "  3. Run: $0 validate"
        ;;
    "create")
        create_env_files
        log_success "Environment files created successfully!"
        echo ""
        log_info "Don't forget to:"
        echo "  1. Set your GOOGLE_API_KEY in .env"
        echo "  2. Adjust other settings as needed"
        ;;
    "validate")
        validate_env_files
        ;;
    "clean")
        clean_env_files
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac