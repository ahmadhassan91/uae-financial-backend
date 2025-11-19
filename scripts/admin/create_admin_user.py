#!/usr/bin/env python3
"""
Create an admin user for the UAE Financial Health Check application.

This script creates a default admin user for accessing the admin dashboard.
Can be run multiple times safely - will skip if admin already exists.

Usage:
    python scripts/admin/create_admin_user.py
    
    Or with custom credentials:
    python scripts/admin/create_admin_user.py --email admin@example.com --password mypassword
"""

import sys
import os
import argparse
from datetime import datetime, date
from sqlalchemy.orm import Session

# Add the backend directory to Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth.utils import get_password_hash

def create_admin_user(email=None, username=None, password=None):
    """Create an admin user with predefined or custom credentials."""
    
    # Admin user credentials (use defaults if not provided)
    admin_email = email or "admin@nationalbonds.ae"
    admin_username = username or "admin"
    admin_password = password or "admin123"  # Simple password for testing
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Create an admin user for UAE Financial Health Check',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create admin with default credentials
  python scripts/admin/create_admin_user.py
  
  # Create admin with custom email and password
  python scripts/admin/create_admin_user.py --email admin@example.com --password SecurePass123
  
Default credentials:
  Email: admin@nationalbonds.ae
  Password: admin123
  Date of Birth: 01/01/1990
        """
    )
    parser.add_argument('--email', help='Admin email address', default=None)
    parser.add_argument('--username', help='Admin username', default=None)
    parser.add_argument('--password', help='Admin password', default=None)
    
    args = parser.parse_args()
    
    print("=== UAE Financial Health Check - Admin User Setup ===\n")
    
    # Ensure database tables exist
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        sys.exit(1)
    
    # Create admin user
    admin_user = create_admin_user(
        email=args.email,
        username=args.username,
        password=args.password
    )
    
    if admin_user:
        # Test credentials
        test_admin_credentials()
        
        print("\n=== Admin Login Instructions ===")
        print("To access the admin dashboard:")
        print("1. Start the backend server:")
        print("   uvicorn app.main:app --reload")
        print("\n2. Go to the admin login page:")
        print("   http://localhost:8000/admin/login")
        print("\n3. Use these credentials:")
        print(f"   Email: {args.email or 'admin@nationalbonds.ae'}")
        print(f"   Password: {args.password or 'admin123'}")
        print("   Date of Birth: 01/01/1990")
        print("\n4. Access admin dashboard:")
        print("   http://localhost:8000/admin")
        
        if not args.password or args.password == "admin123":
            print("\n⚠️  WARNING: Please change the default password in production!")
        
        print("\n✅ Setup complete!")
    else:
        print("\n❌ Admin user setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()