#!/usr/bin/env python3
"""
Create or reset admin users in production database.
This script creates both full admin and view-only admin users.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_admin_users():
    """Create or update admin users in production."""
    
    print("=" * 60)
    print("CREATE/UPDATE ADMIN USERS IN PRODUCTION")
    print("=" * 60)
    print()
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nFor Heroku, run:")
        print("  heroku run python create_production_admin.py --app your-app-name")
        return 1
    
    # Fix Heroku postgres:// to postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"✓ Connecting to database...")
    
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Admin users to create
        admin_users = [
            {
                "email": "admin@nationalbonds.ae",
                "username": "admin",
                "password": "admin123",
                "admin_role": "full",
                "description": "Full Admin"
            },
            {
                "email": "viewonly@nationalbonds.ae",
                "username": "viewonly",
                "password": "viewonly123",
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
            print(f"  Password: {user_data['password']}")
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
        print("\nYou can now login with:")
        print("\n1. Full Admin:")
        print("   Email: admin@nationalbonds.ae")
        print("   Password: admin123")
        print("\n2. View-Only Admin:")
        print("   Email: viewonly@nationalbonds.ae")
        print("   Password: viewonly123")
        print("\n" + "=" * 60)
        
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
