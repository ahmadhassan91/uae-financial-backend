#!/usr/bin/env python3
"""
Create an admin user for the UAE Financial Health Check application.
"""

import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import Session

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth.utils import get_password_hash

def create_admin_user():
    """Create an admin user with predefined credentials."""
    
    # Admin user credentials
    admin_email = "admin@nationalbonds.ae"
    admin_username = "admin"
    admin_password = "admin123"  # Simple password for testing
    admin_dob = date(1990, 1, 1)  # Default date of birth
    
    print("Creating admin user...")
    print(f"Email: {admin_email}")
    print(f"Username: {admin_username}")
    print(f"Password: {admin_password}")
    print(f"Date of Birth: {admin_dob}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == admin_email).first()
        
        if existing_user:
            print(f"✅ Admin user already exists with email: {admin_email}")
            
            # Make sure they are admin
            if not existing_user.is_admin:
                existing_user.is_admin = True
                db.commit()
                print("✅ Updated existing user to admin status")
            
            return existing_user
        
        # Create new admin user
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            email=admin_email,
            username=admin_username,
            hashed_password=hashed_password,
            date_of_birth=datetime.combine(admin_dob, datetime.min.time()),
            is_active=True,
            is_admin=True  # Set admin flag
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   User ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is Admin: {admin_user.is_admin}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        db.rollback()
        return None
        
    finally:
        db.close()

def test_admin_credentials():
    """Test that the admin credentials work."""
    print("\n=== Testing Admin Credentials ===")
    
    db = SessionLocal()
    
    try:
        admin_user = db.query(User).filter(User.email == "admin@nationalbonds.ae").first()
        
        if admin_user:
            print(f"✅ Admin user found:")
            print(f"   ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
            print(f"   Username: {admin_user.username}")
            print(f"   Is Admin: {admin_user.is_admin}")
            print(f"   Is Active: {admin_user.is_active}")
            print(f"   Created: {admin_user.created_at}")
            
            return True
        else:
            print("❌ Admin user not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing admin credentials: {str(e)}")
        return False
        
    finally:
        db.close()

def main():
    """Main function to create admin user and test credentials."""
    print("=== UAE Financial Health Check - Admin User Setup ===")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    # Create admin user
    admin_user = create_admin_user()
    
    if admin_user:
        # Test credentials
        test_admin_credentials()
        
        print("\n=== Admin Login Instructions ===")
        print("To access the admin dashboard:")
        print("1. Go to the login page (/login)")
        print("2. Use these credentials:")
        print("   Email: admin@nationalbonds.ae")
        print("   Date of Birth: 01/01/1990")
        print("3. After login, navigate to /admin")
        print("\n✅ Setup complete!")
    else:
        print("\n❌ Admin user setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()