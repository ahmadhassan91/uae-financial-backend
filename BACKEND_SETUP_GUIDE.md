# Backend Setup Guide - UAE Financial Health Check

This guide will help you set up the backend for the UAE Financial Health Check application from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12** or higher
- **pip** (Python package manager)
- **PostgreSQL** (for production) or SQLite (for development)
- **Git**
- **virtualenv** or **venv** (recommended)

## Quick Setup (Automated)

For a quick automated setup, run the setup script:

```bash
cd backend
chmod +x scripts/setup_backend.sh
./scripts/setup_backend.sh
```

This script will:
- Create a virtual environment
- Install all dependencies
- Set up environment variables
- Initialize the database
- Create an admin user
- Run database migrations

## Manual Setup (Step-by-Step)

If you prefer to set up manually or the automated script fails, follow these steps:

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd uae-financial-health/backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./financial_health.db
# For PostgreSQL (production):
# DATABASE_URL=postgresql://user:password@localhost/financial_health

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Email Configuration (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=UAE Financial Health Check

# Frontend URL
FRONTEND_BASE_URL=http://localhost:3000
# Production:
PRODUCTION_BASE_URL=https://financial-clinic.netlify.app

# Environment
ENVIRONMENT=development
# For production: ENVIRONMENT=production

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# OTP Settings
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=3
```

### Step 5: Initialize the Database

```bash
# Run Alembic migrations to create all tables
alembic upgrade head
```

### Step 6: Create Admin User

```bash
# Run the admin user creation script
python scripts/admin/create_admin_user.py
```

**Default Admin Credentials:**
- Email: `admin@nationalbonds.ae`
- Password: `admin123` (Change this in production!)
- Date of Birth: `01/01/1990`

### Step 7: Start the Development Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Verification Steps

### 1. Check Database Connection

```bash
python -c "from app.database import engine; print('✅ Database connected successfully!')"
```

### 2. Test Admin Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@nationalbonds.ae",
    "password": "admin123"
  }'
```

### 3. Check API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "connected"
}
```

## Database Management

### View Database Schema

```bash
# Using Alembic
alembic current

# Using Python
python -c "from app.models import *; from app.database import engine, Base; print([table for table in Base.metadata.tables.keys()])"
```

### Create New Migration

```bash
# After changing models
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

### Reset Database (Development Only)

```bash
# WARNING: This will delete all data!
rm financial_health.db
alembic upgrade head
python scripts/admin/create_admin_user.py
```

## Testing

### Run All Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Specific Modules

```bash
# Test authentication
pytest tests/test_auth.py -v

# Test Financial Clinic
pytest tests/test_financial_clinic.py -v

# Test scoring
pytest tests/test_scoring.py -v
```

## Common Issues and Solutions

### Issue 1: Module Not Found Error

```bash
# Solution: Ensure you're in the backend directory and virtual environment is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Database Connection Error

```bash
# Solution: Check DATABASE_URL in .env file
# For SQLite, ensure the file path is correct
# For PostgreSQL, verify credentials and server is running
```

### Issue 3: Alembic Migration Conflicts

```bash
# Solution: Reset alembic versions
alembic downgrade base
alembic upgrade head
```

### Issue 4: Port Already in Use

```bash
# Solution: Use a different port or kill the process
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

## Production Deployment

### Heroku Deployment

1. **Install Heroku CLI:**
```bash
brew tap heroku/brew && brew install heroku
```

2. **Login to Heroku:**
```bash
heroku login
```

3. **Create Heroku App:**
```bash
heroku create your-app-name
```

4. **Add PostgreSQL:**
```bash
heroku addons:create heroku-postgresql:mini
```

5. **Set Environment Variables:**
```bash
heroku config:set SECRET_KEY="your-production-secret-key"
heroku config:set ENVIRONMENT="production"
heroku config:set PRODUCTION_BASE_URL="https://your-frontend-url.com"
heroku config:set SENDGRID_API_KEY="your-sendgrid-api-key"
# ... set all other environment variables
```

6. **Deploy:**
```bash
git push heroku main
```

7. **Run Migrations:**
```bash
heroku run alembic upgrade head
```

8. **Create Admin User:**
```bash
heroku run python scripts/admin/create_admin_user.py
```

### Docker Deployment (Optional)

```bash
# Build Docker image
docker build -t uae-financial-health-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  -e SECRET_KEY="your-secret-key" \
  uae-financial-health-backend
```

## Development Workflow

### 1. Start Development Server

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend (in separate terminal)
cd frontend
npm run dev
```

### 2. Making Changes

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Run tests locally
5. Create pull request

### 3. Database Changes

If you modify database models:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Review the migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Test thoroughly
```

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Change default admin password** immediately in production
3. **Use strong SECRET_KEY** - Generate with: `openssl rand -hex 32`
4. **Enable HTTPS** in production
5. **Regularly update dependencies:** `pip install -r requirements.txt --upgrade`
6. **Review security logs** regularly
7. **Implement rate limiting** for API endpoints
8. **Use environment-specific configurations**

## Monitoring and Logs

### View Logs

```bash
# Development
tail -f backend.log

# Heroku Production
heroku logs --tail
```

### Database Backups

```bash
# Backup SQLite (Development)
cp financial_health.db backups/financial_health_$(date +%Y%m%d).db

# Backup PostgreSQL (Production)
heroku pg:backups:capture
heroku pg:backups:download
```

## Support and Resources

- **Project Documentation:** `/docs`
- **API Documentation:** http://localhost:8000/docs
- **Database Schema:** See `/backend/app/models.py`
- **Environment Variables:** See `.env.example`

## Admin Panel Access

After setup, access the admin panel:

1. Start the backend server
2. Login at: http://localhost:8000/admin/login
3. Use admin credentials:
   - Email: `admin@nationalbonds.ae`
   - Password: `admin123` (change in production!)

## Troubleshooting Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check database tables
python -c "from app.database import engine; from app.models import Base; print(Base.metadata.tables.keys())"

# Check Alembic version
alembic current

# Verify admin user exists
python -c "from app.database import SessionLocal; from app.models import User; db=SessionLocal(); admin=db.query(User).filter(User.email=='admin@nationalbonds.ae').first(); print(f'Admin found: {admin.email}' if admin else 'Admin not found')"
```

## Next Steps

After completing the setup:

1. ✅ Verify all tests pass: `pytest tests/ -v`
2. ✅ Change admin password in production
3. ✅ Configure email settings (SendGrid)
4. ✅ Set up frontend connection
5. ✅ Review security settings
6. ✅ Set up monitoring and logging
7. ✅ Create database backups schedule

## Contact

For issues or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs`

---

**Last Updated:** November 2025  
**Version:** 2.0.0
