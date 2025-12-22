#!/bin/bash

echo "Setting up NFS storage for Financial Clinic Backend..."

# Copy NFS config to backend directory
sudo cp scripts/deploy/nfs_config.env /home/finclinic01/backend/

# Update backend service with NFS config
sudo cp scripts/deploy/financialclinic-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Restart backend service
sudo systemctl restart financialclinic-backend

# Check status
sudo systemctl status financialclinic-backend

# Test NFS mount
echo "Testing NFS mount..."
ls -la /mnt/financialclinic/

# Test write access
echo "Testing write access..."
sudo -u finclinic01 touch /mnt/financialclinic/test_write_$(date +%s).txt

echo "NFS storage setup complete!"
echo ""
echo "Backend service status: sudo systemctl status financialclinic-backend"
echo "Backend logs: sudo journalctl -u financialclinic-backend -f"
echo "NFS mount: df -h | grep financialclinic"
