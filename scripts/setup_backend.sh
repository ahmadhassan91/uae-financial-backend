#!/bin/bash

# Backend Setup Script - UAE Financial Health Check
# This script automates the backend setup process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_header "UAE Financial Health Check - Backend Setup"
    
    # Check prerequisites
    print_info "Checking prerequisites..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.12 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
    
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    print_success "pip3 found"
    
    # Navigate to backend directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
    cd "$BACKEND_DIR"
    
    print_info "Working directory: $BACKEND_DIR"
    
    # Step 1: Create Virtual Environment
    print_header "Step 1: Creating Virtual Environment"
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Step 2: Upgrade pip
    print_header "Step 2: Upgrading pip"
    pip install --upgrade pip --quiet
    print_success "pip upgraded"
    
    # Step 3: Install Dependencies
    print_header "Step 3: Installing Dependencies"
    print_info "Installing required packages (this may take a few minutes)..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    pip install -r requirements.txt --quiet
    print_success "All dependencies installed"
    
    # Step 4: Set Up Environment Variables
    print_header "Step 4: Setting Up Environment Variables"
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists. Skipping creation."
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_env_file
        fi
    else
        create_env_file
    fi
    
    # Step 5: Initialize Database
    print_header "Step 5: Initializing Database"
    
    print_info "Running Alembic migrations..."
    alembic upgrade head
    print_success "Database initialized"
    
    # Step 6: Create Admin User
    print_header "Step 6: Creating Admin User"
    
    if [ -f "scripts/admin/create_admin_user.py" ]; then
        print_info "Creating admin user..."
        python scripts/admin/create_admin_user.py
        print_success "Admin user setup complete"
    else
        print_error "Admin user creation script not found!"
        print_warning "You'll need to create an admin user manually."
    fi
    
    # Step 7: Verify Setup
    print_header "Step 7: Verifying Setup"
    
    print_info "Checking database connection..."
    python -c "from app.database import engine; print('Database connected successfully!')" 2>/dev/null && print_success "Database connection verified" || print_error "Database connection failed"
    
    print_info "Checking admin user..."
    python -c "from app.database import SessionLocal; from app.models import User; db=SessionLocal(); admin=db.query(User).filter(User.email=='admin@nationalbonds.ae').first(); print(f'Admin user: {admin.email}' if admin else 'Admin user not found'); db.close()" 2>/dev/null && print_success "Admin user verified" || print_warning "Admin user verification failed"
    
    # Final Instructions
    print_header "Setup Complete! 🎉"
    
    echo ""
    print_success "Backend setup completed successfully!"
    echo ""
    print_info "Next Steps:"
    echo "  1. Review and update .env file with your configuration"
    echo "  2. Start the development server:"
    echo "     ${GREEN}source venv/bin/activate${NC}"
    echo "     ${GREEN}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
    echo ""
    echo "  3. Access the API:"
    echo "     - API: http://localhost:8000"
    echo "     - Docs: http://localhost:8000/docs"
    echo "     - Admin: http://localhost:3000/admin"
    echo ""
    print_info "Default Admin Users:"
    echo ""
    echo "  ${GREEN}Full Admin${NC} (can view and modify all data):"
    echo "    - Email: admin@nationalbonds.ae"
    echo "    - Password: admin123"
    echo "    - Date of Birth: 01/01/1990"
    echo ""
    echo "  ${YELLOW}View-Only Admin${NC} (read-only access):"
    echo "    - Email: viewonly@nationalbonds.ae"
    echo "    - Password: viewonly123"
    echo "    - Date of Birth: 01/01/1990"
    echo ""
    echo "  ${YELLOW}⚠️  Change these passwords in production!${NC}"
    echo ""
    print_info "To reset a password:"
    echo "     ${GREEN}python scripts/admin/create_admin_user.py --reset-password admin@nationalbonds.ae --new-password YourNewPassword${NC}"
    echo ""
    print_info "For detailed documentation, see: BACKEND_SETUP_GUIDE.md"
    echo ""
}

# Create .env file
create_env_file() {
    print_info "Creating .env file..."
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./financial_health.db
# For PostgreSQL (production):
# DATABASE_URL=postgresql://user:password@localhost/financial_health

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Email Configuration (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=UAE Financial Health Check

# Frontend URL
FRONTEND_BASE_URL=http://localhost:3000
PRODUCTION_BASE_URL=https://financial-clinic.netlify.app

# Environment
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# OTP Settings
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=3
EOF
    
    print_success ".env file created with random SECRET_KEY"
    print_warning "Please update the .env file with your actual configuration (SendGrid API key, etc.)"
}

# Run main function
main

# Deactivate virtual environment at the end
deactivate 2>/dev/null || true
