# On-Prem Deployment Guide for Financial Clinic (National Bonds)

## Overview

This guide explains how to deploy the Financial Clinic application on National Bonds' on-prem server at `192.168.128.135`.

---

## Architecture

```
Users Access
     ↓
https://financialclinic.ae (Nginx - Reverse Proxy at 192.168.128.135)
     ├── / → Frontend Static Files (/var/www/financialclinic/out)
     ├── /api/* → Backend FastAPI (http://192.168.128.135:8000)
     └── /storage/* → NFS Mount (/mnt/financialclinic)
```

---

## Prerequisites

- Nginx installed on the on-prem server
- SSL certificate for `financialclinic.ae` (from Let's Encrypt or your CA)
- NFS mount configured: `/mnt/financialclinic`
- Backend running on port 8000
- PostgreSQL database
- Python 3.10+

---

## Deployment Steps

### Step 1: Build Frontend for Static Export

On your local machine or CI server:

```bash
cd frontend

# Copy on-prem environment
cp .env.onprem.example .env.local

# Install dependencies
npm install

# Build static export
npm run build

# This creates the 'out' folder with all static files
```

### Step 2: Deploy Frontend to On-Prem Server

```bash
# Create deployment package
tar -czf financialclinic_frontend.tar.gz -C out .

# Copy to server
scp financialclinic_frontend.tar.gz finclinic01@192.168.128.135:/tmp/

# On the server, extract to web root
ssh finclinic01@192.168.128.135
sudo mkdir -p /var/www/financialclinic/out
sudo tar -xzf /tmp/financialclinic_frontend.tar.gz -C /var/www/financialclinic/out
sudo chown -R www-data:www-data /var/www/financialclinic
```

### Step 3: Configure Backend

On the on-prem server:

```bash
cd /home/finclinic01/projects/uae-financial-backend

# Copy on-prem environment
cp .env.onprem.example .env

# Edit .env with server-specific values:
# - DATABASE_URL (PostgreSQL connection)
# - SECRET_KEY (generate new secure key)
# - NFS paths if different
nano .env

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Configure Nginx

On the on-prem server:

```bash
# Copy Nginx config
sudo cp nginx.conf.onprem.example /etc/nginx/sites-available/financialclinic.ae

# Enable the site
sudo ln -sf /etc/nginx/sites-available/financialclinic.ae /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null || true

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 5: Set Up SSL Certificate

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate from Let's Encrypt
sudo certbot certonly -d financialclinic.ae -d www.financialclinic.ae --webroot -w /var/www/financialclinic/out

# Auto-renewal (already enabled by certbot)
sudo systemctl enable certbot.timer
```

### Step 6: Configure NFS Mount

```bash
# Create mount point
sudo mkdir -p /mnt/financialclinic

# Mount NFS share (from National Bonds NFS server)
sudo mount -t nfs 192.168.125.35:/financialclinic /mnt/financialclinic

# Make permanent in /etc/fstab
echo "192.168.125.35:/financialclinic /mnt/financialclinic nfs defaults 0 0" | sudo tee -a /etc/fstab

# Verify mount
mount | grep financialclinic
```

### Step 7: Verify Deployment

```bash
# Test frontend
curl -I https://financialclinic.ae

# Test API
curl -I https://financialclinic.ae/api/v1/health

# Check Nginx logs
sudo tail -f /var/log/nginx/financialclinic_access.log
sudo tail -f /var/log/nginx/financialclinic_error.log

# Check backend logs
tail -f /home/finclinic01/projects/uae-financial-backend/logs/app.log
```

---

## Environment Variables

### Backend (.env)

Key variables for on-prem:

```properties
# Must be 'production'
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/financial_clinic

# Storage - Use NFS, not S3
USE_S3_STORAGE=false
USE_NFS_STORAGE=true
NFS_MOUNT_PATH=/mnt/financialclinic
NFS_PUBLIC_URL_BASE=https://financialclinic.ae/storage

# URLs via Nginx proxy
BACKEND_BASE_URL=https://financialclinic.ae/api
PRODUCTION_BACKEND_URL=https://financialclinic.ae/api
FRONTEND_BASE_URL=https://financialclinic.ae
PRODUCTION_BASE_URL=https://financialclinic.ae

# Email - Internal relay
SMTP_HOST=smtprelay.nationalbonds.ae
SMTP_PORT=25
SMTP_PASSWORD=

# CORS
CORS_ORIGINS=https://financialclinic.ae,https://www.financialclinic.ae
```

### Frontend (.env.local during build)

```properties
NEXT_PUBLIC_API_URL=https://financialclinic.ae/api/v1
NEXT_PUBLIC_BASE_URL=https://financialclinic.ae
NEXT_PUBLIC_ENVIRONMENT=production
STATIC_EXPORT=true
```

---

## URL Routing

All requests go through Nginx to the appropriate service:

| URL | Routes To | Example |
|-----|-----------|---------|
| `https://financialclinic.ae/` | Frontend | Homepage |
| `https://financialclinic.ae/financial-clinic/survey` | Frontend | Survey page |
| `https://financialclinic.ae/api/v1/health` | Backend | API health check |
| `https://financialclinic.ae/api/v1/auth/login` | Backend | Login endpoint |
| `https://financialclinic.ae/storage/reports/2025-12-17_report.pdf` | NFS | PDF reports |

---

## Troubleshooting

### Mixed Content Errors

**Problem:** `https://financialclinic.ae` (HTTPS) calls `http://192.168.128.135:8000` (HTTP)

**Solution:** Already configured! The Nginx proxy handles this. Frontend calls `https://financialclinic.ae/api/v1` which proxies to HTTP backend internally.

### SSL Certificate Errors

```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check renewal log
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### NFS Mount Issues

```bash
# Check mount status
mount | grep financialclinic

# Remount if disconnected
sudo umount /mnt/financialclinic
sudo mount -t nfs 192.168.125.35:/financialclinic /mnt/financialclinic

# Check permissions
sudo ls -la /mnt/financialclinic
```

### Backend Connection Issues

```bash
# Check if backend is running
netstat -tlnp | grep 8000

# Check backend logs
tail -f /home/finclinic01/projects/uae-financial-backend/logs/app.log

# Test backend directly
curl http://192.168.128.135:8000/api/v1/health
```

### Nginx Configuration Errors

```bash
# Validate config
sudo nginx -t

# Reload after fix
sudo systemctl reload nginx

# Check Nginx status
sudo systemctl status nginx
```

---

## File Locations

```
Frontend:
  /var/www/financialclinic/out           → Served by Nginx

Backend:
  /home/finclinic01/projects/uae-financial-backend
  ├── .env                               → Configuration
  ├── app/main.py                        → FastAPI app
  └── logs/
      ├── app.log                        → All logs
      └── errors.log                     → Error logs only

NFS Storage:
  /mnt/financialclinic/
  ├── reports/                           → PDF reports
  └── icons/                             → Static icons

Nginx:
  /etc/nginx/sites-available/financialclinic.ae
  /var/log/nginx/financialclinic_*.log

SSL Certificates:
  /etc/letsencrypt/live/financialclinic.ae/
```

---

## Updating the Application

### Update Frontend

```bash
# On local machine
cd frontend
git pull origin feature/financial-clinic-survey
cp .env.onprem.example .env.local
npm install
npm run build

# Deploy to server
tar -czf financialclinic_frontend_new.tar.gz -C out .
scp financialclinic_frontend_new.tar.gz finclinic01@192.168.128.135:/tmp/

# On server
sudo rm -rf /var/www/financialclinic/out/*
sudo tar -xzf /tmp/financialclinic_frontend_new.tar.gz -C /var/www/financialclinic/out
sudo chown -R www-data:www-data /var/www/financialclinic
```

### Update Backend

```bash
# On server
cd /home/finclinic01/projects/uae-financial-backend
git pull origin feature/financial-clinic-survey
pip install -r requirements.txt
alembic upgrade head

# Restart backend
sudo systemctl restart uvicorn
```

---

## Monitoring

### Check Application Health

```bash
# Frontend
curl -I https://financialclinic.ae

# Backend
curl https://financialclinic.ae/api/v1/health

# Check logs
sudo journalctl -u nginx -f
tail -f /home/finclinic01/projects/uae-financial-backend/logs/app.log
```

### Performance Monitoring

```bash
# Monitor server resources
htop

# Check disk usage (especially NFS)
df -h

# Check connections
netstat -an | grep ESTABLISHED | wc -l
```

---

## Backup & Recovery

### Backup Database

```bash
pg_dump financial_clinic > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Backup NFS Files

```bash
tar -czf nfs_backup_$(date +%Y%m%d_%H%M%S).tar.gz /mnt/financialclinic/
```

### Backup Frontend Build

```bash
tar -czf frontend_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/financialclinic/out/
```

---

## Support

For issues, check:
1. `/var/log/nginx/financialclinic_*.log` - Nginx logs
2. `/home/finclinic01/projects/uae-financial-backend/logs/app.log` - Backend logs
3. `sudo journalctl -u nginx -xe` - Systemd logs

---

**Last Updated:** December 17, 2025
**Version:** 1.0
