# Backend Scripts

This directory contains utility scripts for managing the UAE Financial Health Check backend.

## Setup Scripts

### `setup_backend.sh`
Automated setup script that configures the entire backend environment.

**Usage:**
```bash
cd backend
chmod +x scripts/setup_backend.sh
./scripts/setup_backend.sh
```

**What it does:**
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Creates .env file with secure defaults
- Runs database migrations
- Creates default admin user
- Verifies the setup

**Requirements:**
- Python 3.12+
- pip3
- Internet connection (for package installation)

---

### `start.sh`
Quick start script for running the development server.

**Usage:**
```bash
cd backend
chmod +x scripts/start.sh
./scripts/start.sh
```

**What it does:**
- Activates virtual environment
- Checks for .env file
- Starts the FastAPI development server on port 8000

**Prerequisites:**
- Backend must be set up first (run `setup_backend.sh`)
- .env file must exist

---

## Admin Scripts

### `admin/create_admin_user.py`
Creates an admin user for accessing the admin dashboard.

**Basic Usage:**
```bash
cd backend
source venv/bin/activate
python scripts/admin/create_admin_user.py
```

**With Custom Credentials:**
```bash
python scripts/admin/create_admin_user.py \
  --email admin@example.com \
  --username myadmin \
  --password SecurePassword123
```

**Options:**
- `--email`: Admin email address (default: admin@nationalbonds.ae)
- `--username`: Admin username (default: admin)
- `--password`: Admin password (default: admin123)

**Default Credentials:**
- Email: `admin@nationalbonds.ae`
- Password: `admin123`
- Date of Birth: `01/01/1990`

⚠️ **Security Note:** Change the default password in production!

---

## Common Workflows

### First Time Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd uae-financial-health/backend

# 2. Run automated setup
./scripts/setup_backend.sh

# 3. Update .env with your configuration
nano .env

# 4. Start the server
./scripts/start.sh
```

### Daily Development

```bash
# Start the server
cd backend
./scripts/start.sh

# Or manually:
source venv/bin/activate
uvicorn app.main:app --reload
```

### Reset Database (Development Only)

```bash
cd backend
source venv/bin/activate

# Delete the database
rm financial_health.db

# Run migrations
alembic upgrade head

# Recreate admin user
python scripts/admin/create_admin_user.py
```

### Update Dependencies

```bash
cd backend
source venv/bin/activate

# Update all packages
pip install -r requirements.txt --upgrade

# Or update specific package
pip install package-name --upgrade
```

### Create Database Backup

```bash
cd backend

# SQLite (development)
cp financial_health.db backups/backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL (production)
pg_dump -U username -h hostname database_name > backup.sql
```

---

## Troubleshooting

### Script Permission Denied

```bash
chmod +x scripts/setup_backend.sh
chmod +x scripts/start.sh
chmod +x scripts/admin/create_admin_user.py
```

### Virtual Environment Not Found

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Migration Issues

```bash
# Check current version
alembic current

# Reset to base
alembic downgrade base

# Apply all migrations
alembic upgrade head
```

### Admin User Already Exists

The script will skip creation if the admin user already exists. To update:

```bash
# Option 1: Use Python console
python
>>> from app.database import SessionLocal
>>> from app.models import User
>>> db = SessionLocal()
>>> admin = db.query(User).filter(User.email == 'admin@nationalbonds.ae').first()
>>> admin.is_admin = True
>>> db.commit()
>>> exit()

# Option 2: Delete and recreate
python
>>> from app.database import SessionLocal
>>> from app.models import User
>>> db = SessionLocal()
>>> db.query(User).filter(User.email == 'admin@nationalbonds.ae').delete()
>>> db.commit()
>>> exit()
# Then run create_admin_user.py again
```

---

## Script Development

### Adding New Scripts

1. Create script in appropriate subdirectory:
   - `scripts/` - General utilities
   - `scripts/admin/` - Admin-related scripts
   - `scripts/database/` - Database management scripts

2. Add shebang line:
   ```python
   #!/usr/bin/env python3
   ```
   or
   ```bash
   #!/bin/bash
   ```

3. Make executable:
   ```bash
   chmod +x scripts/your-script.py
   ```

4. Document in this README

### Best Practices

- Use descriptive names
- Add help text and documentation
- Handle errors gracefully
- Provide clear output messages
- Test in clean environment
- Update this README

---

## Environment Variables

All scripts respect the following environment variables:

- `PYTHONPATH` - Python module search path
- `DATABASE_URL` - Database connection string
- `ENVIRONMENT` - Current environment (development/production)

Load from .env:
```bash
source .env
```

---

## Support

For issues or questions:
- Check `BACKEND_SETUP_GUIDE.md` for detailed documentation
- Review error messages carefully
- Check logs in `backend.log`
- Ensure all prerequisites are installed

---

**Last Updated:** November 2025
**Maintainer:** Development Team
