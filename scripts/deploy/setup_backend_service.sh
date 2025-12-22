#!/bin/bash

# Setup Financial Clinic Backend as systemd service
# Run with: sudo bash setup_backend_service.sh

echo "Setting up Financial Clinic Backend service..."

# Copy service file
sudo cp financialclinic-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable financialclinic-backend

# Start the service
sudo systemctl start financialclinic-backend

# Check status
sudo systemctl status financialclinic-backend

echo ""
echo "Backend service setup complete!"
echo ""
echo "To check logs: sudo journalctl -u financialclinic-backend -f"
echo "To restart: sudo systemctl restart financialclinic-backend"
echo "To stop: sudo systemctl stop financialclinic-backend"
