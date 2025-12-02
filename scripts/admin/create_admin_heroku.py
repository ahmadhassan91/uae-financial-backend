#!/usr/bin/env python3
"""Create admin user for Heroku using the same method as local."""

from app.database import SessionLocal
from app.models import User
from app.auth.utils import get_password_hash
from datetime import date, datetime

def create_admin_user():
    """Create admin user using the same method as local."""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.email == 'admin@nationalbonds.ae').first()
        if existing_admin:
            print('✅ Admin user already exists')
            print('Email: admin@nationalbonds.ae')
            print('🔗 Access admin at: https://uae-financial-health-api-4188fd6ae86c.herokuapp.com/admin')
            return
        
        # Create admin user using the same method as local
        admin_email = "admin@nationalbonds.ae"
        admin_username = "admin"
        admin_password = "admin123"
        admin_dob = date(1990, 1, 1)
        
        print(f"Creating admin user...")
        print(f"Email: {admin_email}")
        print(f"Username: {admin_username}")
        print(f"Password: {admin_password}")
        print(f"Date of Birth: {admin_dob}")
        
        # Use the same password hashing as local
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            email=admin_email,
            username=admin_username,
            hashed_password=hashed_password,
            date_of_birth=datetime.combine(admin_dob, datetime.min.time()),
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print('✅ Admin user created successfully!')
        print(f'   User ID: {admin_user.id}')
        print(f'   Email: {admin_user.email}')
        print(f'   Is Admin: {admin_user.is_admin}')
        print('🔗 Access admin at: https://uae-financial-health-api-4188fd6ae86c.herokuapp.com/admin')
        
    except Exception as e:
        print(f'❌ Error creating admin user: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_admin_user()