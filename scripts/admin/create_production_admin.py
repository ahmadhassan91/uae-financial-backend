#!/usr/bin/env python3
"""
Create or reset admin users in production database.
This script creates both full admin and view-only admin users.
SECURE VERSION: No hardcoded credentials.
"""
import os
import sys
import getpass
import secrets
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def get_secure_password(prompt: str, env_var: str = None) -> str:
    """
    Get a password securely from env var, user input, or generate one.
    """
    if env_var:
        pwd = os.getenv(env_var)
        if pwd:
            return pwd
            
    print(f"\n--- {prompt} ---")
    print("1. Enter password manually")
    print("2. Generate secure random password")
    
    while True:
        choice = input("Select option (1/2): ").strip()
        if choice == "1":
            pwd = getpass.getpass("Enter password: ")
            confirm = getpass.getpass("Confirm password: ")
            if pwd != confirm:
                print("Passwords do not match. Try again.")
                continue
            if len(pwd) < 8:
                print("Password too short. Must be at least 8 characters.")
                continue
            return pwd
        elif choice == "2":
            pwd = secrets.token_urlsafe(16)
            print(f"Generated password: {pwd}")
            print("⚠️  SAVE THIS PASSWORD NOW - IT WILL NOT BE SHOWN AGAIN ⚠️")
            input("Press Enter when you have saved the password...")
            return pwd
        else:
            print("Invalid choice.")


def create_admin_users():
    """Create or update admin users in production."""
    
    print("=" * 60)
    print("CREATE/UPDATE ADMIN USERS IN PRODUCTION (SECURE)")
    print("=" * 60)
    print()
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nFor Heroku, run:")
        print("  heroku run python scripts/admin/create_production_admin.py --app your-app-name")
        return 1
    
    # Fix Heroku postgres:// to postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"✓ Connecting to database...")
    
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Get Admin Passwords
        print("\n🔐 CREDENTIAL SETUP")
        
        print("\n[Full Admin User]")
        admin_email = input("Enter email for Full Admin (default: admin@nationalbonds.ae): ").strip() or "admin@nationalbonds.ae"
        admin_password = get_secure_password("Full Admin Password", "ADMIN_PASSWORD")
        
        print("\n[View-Only Admin User]")
        view_email = input("Enter email for View-Only Admin (default: viewonly@nationalbonds.ae): ").strip() or "viewonly@nationalbonds.ae"
        view_password = get_secure_password("View-Only Admin Password", "VIEWONLY_PASSWORD")
        
        # Admin users to create
        admin_users = [
            {
                "email": admin_email,
                "username": "admin",
                "password": admin_password,
                "admin_role": "full",
                "description": "Full Admin"
            },
            {
                "email": view_email,
                "username": "viewonly",
                "password": view_password,
                "admin_role": "view_only",
                "description": "View-Only Admin"
            }
        ]
        
        print("\n" + "=" * 60)
        print("Creating/Updating Admin Users")
        print("=" * 60)
        
        for user_data in admin_users:
            print(f"\n{user_data['description']}:")
            print(f"  Email: {user_data['email']}")
            print(f"  Role: {user_data['admin_role']}")
            
            # Check if user exists
            result = db.execute(text("""
                SELECT id, email, is_admin, admin_role 
                FROM users 
                WHERE email = :email
            """), {"email": user_data['email']})
            
            existing_user = result.fetchone()
            
            # Hash the password
            hashed_password = get_password_hash(user_data['password'])
            
            if existing_user:
                print(f"  ✓ User exists (ID: {existing_user[0]}), updating...")
                
                # Update existing user
                db.execute(text("""
                    UPDATE users 
                    SET 
                        username = :username,
                        hashed_password = :hashed_password,
                        is_admin = true,
                        admin_role = :admin_role,
                        is_active = true,
                        email_verified = true
                    WHERE email = :email
                """), {
                    "email": user_data['email'],
                    "username": user_data['username'],
                    "hashed_password": hashed_password,
                    "admin_role": user_data['admin_role']
                })
                db.commit()
                print(f"  ✓ Updated successfully!")
                
            else:
                print(f"  ✓ User doesn't exist, creating...")
                
                # Create new user
                db.execute(text("""
                    INSERT INTO users (
                        email, 
                        username, 
                        hashed_password, 
                        is_admin, 
                        admin_role, 
                        is_active, 
                        email_verified,
                        created_at
                    )
                    VALUES (
                        :email,
                        :username,
                        :hashed_password,
                        true,
                        :admin_role,
                        true,
                        true,
                        NOW()
                    )
                """), {
                    "email": user_data['email'],
                    "username": user_data['username'],
                    "hashed_password": hashed_password,
                    "admin_role": user_data['admin_role']
                })
                db.commit()
                print(f"  ✓ Created successfully!")
        
        # Verify all admin users
        print("\n" + "=" * 60)
        print("Verification - All Admin Users:")
        print("=" * 60)
        
        result = db.execute(text("""
            SELECT id, email, username, is_admin, admin_role, is_active, email_verified
            FROM users 
            WHERE is_admin = true
            ORDER BY id
        """))
        
        admins = result.fetchall()
        
        if admins:
            for admin in admins:
                print(f"\n  ID: {admin[0]}")
                print(f"  Email: {admin[1]}")
                print(f"  Username: {admin[2]}")
                print(f"  Is Admin: {admin[3]}")
                print(f"  Admin Role: {admin[4]}")
                print(f"  Is Active: {admin[5]}")
                print(f"  Email Verified: {admin[6]}")
        else:
            print("  ❌ No admin users found!")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("✓ SUCCESS! Admin users created/updated")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    return create_admin_users()


if __name__ == "__main__":
    sys.exit(main())
