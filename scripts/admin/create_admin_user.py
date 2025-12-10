#!/usr/bin/env python3
"""
Create admin users for the UAE Financial Health Check application.

This script creates default admin users (full admin and view-only admin) for 
accessing the admin dashboard. Can be run multiple times safely - will skip 
if admin already exists.

Usage:
    python scripts/admin/create_admin_user.py
    
    Or with custom credentials:
    python scripts/admin/create_admin_user.py --email admin@example.com --password mypassword
    
    Create view-only admin:
    python scripts/admin/create_admin_user.py --email viewer@example.com --password mypassword --role view_only
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


# Default admin users configuration
DEFAULT_ADMIN_USERS = [
    {
        "email": "admin@nationalbonds.ae",
        "username": "admin",
        "password": "admin123",
        "admin_role": "full",
        "description": "Full Admin (can view and modify all data)"
    },
    {
        "email": "viewonly@nationalbonds.ae",
        "username": "viewonly",
        "password": "viewonly123",
        "admin_role": "view_only",
        "description": "View-Only Admin (can only view data, no modifications)"
    }
]


def create_admin_user(email: str, username: str, password: str, admin_role: str = "full", db: Session = None):
    """Create an admin user with specified credentials and role."""
    
    admin_dob = date(1990, 1, 1)  # Default date of birth
    close_db = False
    
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            print(f"  ⚠️  User already exists: {email}")
            
            # Update admin status and role if needed
            updated = False
            if not existing_user.is_admin:
                existing_user.is_admin = True
                updated = True
            
            if hasattr(existing_user, 'admin_role') and existing_user.admin_role != admin_role:
                existing_user.admin_role = admin_role
                updated = True
            
            if updated:
                db.commit()
                print(f"  ✅ Updated user to admin with role: {admin_role}")
            else:
                print(f"  ✅ User already has correct admin settings")
            
            return existing_user
        
        # Create new admin user
        hashed_password = get_password_hash(password)
        
        admin_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            date_of_birth=datetime.combine(admin_dob, datetime.min.time()),
            is_active=True,
            is_admin=True,
            admin_role=admin_role
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"  ✅ Created: {email} (Role: {admin_role})")
        
        return admin_user
        
    except Exception as e:
        print(f"  ❌ Error creating user {email}: {str(e)}")
        db.rollback()
        return None
        
    finally:
        if close_db:
            db.close()


def create_all_default_admins():
    """Create all default admin users."""
    print("\n📋 Creating Default Admin Users...")
    print("=" * 50)
    
    db = SessionLocal()
    created_users = []
    
    try:
        for user_config in DEFAULT_ADMIN_USERS:
            print(f"\n{user_config['description']}:")
            user = create_admin_user(
                email=user_config['email'],
                username=user_config['username'],
                password=user_config['password'],
                admin_role=user_config['admin_role'],
                db=db
            )
            if user:
                created_users.append({
                    **user_config,
                    'id': user.id
                })
    finally:
        db.close()
    
    return created_users


def list_admin_users():
    """List all admin users in the database."""
    print("\n📋 Current Admin Users:")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        admin_users = db.query(User).filter(User.is_admin == True).all()
        
        if not admin_users:
            print("  No admin users found.")
            return []
        
        for user in admin_users:
            role = getattr(user, 'admin_role', 'full')
            print(f"  • {user.email}")
            print(f"    ID: {user.id}")
            print(f"    Username: {user.username}")
            print(f"    Role: {role}")
            print(f"    Active: {user.is_active}")
            print(f"    Created: {user.created_at}")
            print()
        
        return admin_users
        
    finally:
        db.close()


def reset_admin_password(email: str, new_password: str):
    """Reset password for an admin user."""
    print(f"\n🔑 Resetting password for: {email}")
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"  ❌ User not found: {email}")
            return False
        
        if not user.is_admin:
            print(f"  ❌ User is not an admin: {email}")
            return False
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        print(f"  ✅ Password reset successfully for: {email}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error resetting password: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()


def main():
    """Main function to create admin users."""
    parser = argparse.ArgumentParser(
        description='Manage admin users for UAE Financial Health Check',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create all default admin users (full admin + view-only)
  python scripts/admin/create_admin_user.py
  
  # Create a custom admin with full access
  python scripts/admin/create_admin_user.py --email admin@example.com --password SecurePass123
  
  # Create a view-only admin
  python scripts/admin/create_admin_user.py --email viewer@example.com --password SecurePass123 --role view_only
  
  # List all admin users
  python scripts/admin/create_admin_user.py --list
  
  # Reset admin password
  python scripts/admin/create_admin_user.py --reset-password admin@nationalbonds.ae --new-password NewSecurePass123

Default Admin Users:
  1. Full Admin
     Email: admin@nationalbonds.ae
     Password: admin123
     
  2. View-Only Admin
     Email: viewonly@nationalbonds.ae
     Password: viewonly123
        """
    )
    parser.add_argument('--email', help='Admin email address')
    parser.add_argument('--username', help='Admin username')
    parser.add_argument('--password', help='Admin password')
    parser.add_argument('--role', choices=['full', 'view_only'], default='full',
                        help='Admin role (default: full)')
    parser.add_argument('--list', action='store_true', help='List all admin users')
    parser.add_argument('--reset-password', metavar='EMAIL', help='Reset password for admin user')
    parser.add_argument('--new-password', help='New password (use with --reset-password)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  UAE Financial Health Check - Admin User Management")
    print("=" * 60)
    
    # Ensure database tables exist
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        sys.exit(1)
    
    # Handle different commands
    if args.list:
        list_admin_users()
        return
    
    if args.reset_password:
        if not args.new_password:
            print("❌ Error: --new-password is required with --reset-password")
            sys.exit(1)
        success = reset_admin_password(args.reset_password, args.new_password)
        sys.exit(0 if success else 1)
    
    if args.email:
        # Create custom admin user
        username = args.username or args.email.split('@')[0]
        password = args.password or 'admin123'
        
        print(f"\n📋 Creating Custom Admin User...")
        print("=" * 50)
        print(f"  Email: {args.email}")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password)}")
        print(f"  Role: {args.role}")
        
        user = create_admin_user(
            email=args.email,
            username=username,
            password=password,
            admin_role=args.role
        )
        
        if not user:
            sys.exit(1)
    else:
        # Create all default admin users
        created_users = create_all_default_admins()
        
        if not created_users:
            print("\n❌ No admin users were created!")
            sys.exit(1)
    
    # Show all admin users
    list_admin_users()
    
    # Show login instructions
    print("\n" + "=" * 60)
    print("  Admin Login Instructions")
    print("=" * 60)
    print("""
1. Start the backend server:
   uvicorn app.main:app --reload

2. Go to the admin login page:
   http://localhost:3000/admin

3. Use these credentials:

   Full Admin (can modify data):
   • Email: admin@nationalbonds.ae
   • Password: admin123
   • Date of Birth: 01/01/1990

   View-Only Admin (read-only access):
   • Email: viewonly@nationalbonds.ae
   • Password: viewonly123
   • Date of Birth: 01/01/1990

⚠️  WARNING: Change these passwords in production!

To change a password:
   python scripts/admin/create_admin_user.py --reset-password admin@nationalbonds.ae --new-password YourSecurePassword
""")
    
    print("✅ Setup complete!")


if __name__ == "__main__":
    main()