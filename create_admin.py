#!/usr/bin/env python3
"""Create admin user for the system."""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
import bcrypt

def create_admin_user():
    """Create default admin user."""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@nationalbonds.ae").first()
        
        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Username: {existing_admin.username}")
            print(f"   Is Admin: {existing_admin.is_admin}")
            return existing_admin
        
        # Create new admin user
        hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin_user = User(
            email="admin@nationalbonds.ae",
            username="admin",
            hashed_password=hashed_password,
            date_of_birth=datetime(1990, 1, 1),
            is_active=True,
            is_admin=True,
            email_verified=True,
            email_verified_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Email: admin@nationalbonds.ae")
        print(f"   Password: admin123")
        print(f"   Date of Birth: 01/01/1990")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
