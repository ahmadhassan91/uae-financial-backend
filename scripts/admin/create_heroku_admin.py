#!/usr/bin/env python3
"""Create admin user for Heroku deployment."""

from app.database import SessionLocal
from app.models import User
import hashlib
from datetime import date

def create_admin_user():
    """Create admin user if it doesn't exist."""
    # Simple hash for admin user creation
    db = SessionLocal()
    
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.email == 'admin@nationalbonds.ae').first()
        if existing_admin:
            print('✅ Admin user already exists')
            print('Email: admin@nationalbonds.ae')
            return
        
        # Create admin user with simple hash (for initial setup only)
        password = 'admin123'
        # Use a simple hash for now - admin should change password after first login
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        admin_user = User(
            email='admin@nationalbonds.ae',
            username='admin',
            hashed_password=hashed_password,
            date_of_birth=date(1990, 1, 1),
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print('✅ Admin user created successfully!')
        print('Email: admin@nationalbonds.ae')
        print('Password: admin123')
        print('🔗 Access admin at: https://uae-financial-health-api-4188fd6ae86c.herokuapp.com/admin')
        
    except Exception as e:
        print(f'❌ Error creating admin user: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_admin_user()