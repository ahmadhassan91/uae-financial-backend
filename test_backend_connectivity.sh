#!/bin/bash
# Backend Connectivity Test Script
# Run this on the on-prem server to diagnose the issue

echo "=========================================="
echo "Backend Connectivity Diagnostic"
echo "=========================================="
echo ""

# 1. Check if backend service is running
echo "1. Checking if python.service is running..."
sudo systemctl status python.service | grep "Active:"
echo ""

# 2. Check if backend is listening on port 8000
echo "2. Checking if backend is listening on port 8000..."
netstat -tlnp 2>/dev/null | grep :8000 || ss -tlnp 2>/dev/null | grep :8000
echo ""

# 3. Test backend health endpoint directly
echo "3. Testing backend health endpoint (localhost:8000)..."
curl -s http://localhost:8000/api/v1/health | head -20
echo ""
echo ""

# 4. Test incomplete survey endpoint directly
echo "4. Testing incomplete survey endpoint (localhost:8000)..."
curl -s -X POST http://localhost:8000/api/v1/surveys/incomplete/start-guest \
  -H "Content-Type: application/json" \
  -d '{"current_step":0,"total_steps":14,"responses":{}}' | head -20
echo ""
echo ""

# 5. Check nginx configuration
echo "5. Checking nginx configuration..."
sudo nginx -t
echo ""

# 6. Check nginx is running
echo "6. Checking if nginx is running..."
sudo systemctl status nginx | grep "Active:"
echo ""

# 7. Test through nginx proxy
echo "7. Testing through nginx proxy (https://financialclinic.ae)..."
curl -s https://financialclinic.ae/api/v1/health | head -20
echo ""
echo ""

# 8. Check backend logs
echo "8. Recent backend logs (last 20 lines)..."
sudo journalctl -u python.service -n 20 --no-pager
echo ""

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
