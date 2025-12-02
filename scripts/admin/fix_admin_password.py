#!/usr/bin/env python3
"""
Fix admin password issue on Heroku
This script recreates the admin user with the correct password to fix bcrypt issues
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models import User
from app.database import Base

def fix_admin_password():
    """Fix the admin password issue."""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        return False
    
    # Fix Heroku postgres URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"🔗 Connecting to database...")
    
    try:
        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create password context
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        with SessionLocal() as db:
            # Find existing admin user
            admin_user = db.query(User).filter(User.email == "admin@nationalbonds.ae").first()
            
            if admin_user:
                print(f"📝 Found existing admin user: {admin_user.email}")
                
                # Update password with proper hashing
                new_password = "admin123"
                
                # Ensure password is within bcrypt limits (72 bytes)
                if len(new_password.encode('utf-8')) > 72:
                    print("❌ Password too long for bcrypt")
                    return False
                
                # Hash the password
                hashed_password = pwd_context.hash(new_password)
                print(f"🔐 Generated new password hash")
                
                # Update the user
                admin_user.hashed_password = hashed_password
                admin_user.is_admin = True
                admin_user.is_active = True
                
                db.commit()
                
                print("✅ Admin password updated successfully!")
                print(f"📧 Email: admin@nationalbonds.ae")
                print(f"🔑 Password: admin123")
                
                # Test the password
                if pwd_context.verify(new_password, admin_user.hashed_password):
                    print("✅ Password verification test passed!")
                else:
                    print("❌ Password verification test failed!")
                    return False
                
                return True
            else:
                print("❌ Admin user not found")
                return False
                
    except Exception as e:
        print(f"❌ Error fixing admin password: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing admin password issue...")
    print("=" * 50)
    
    success = fix_admin_password()
    
    if success:
        print("\n🎉 Admin password fixed successfully!")
        print("You can now login with:")
        print("Email: admin@nationalbonds.ae")
        print("Password: admin123")
    else:
        print("\n❌ Failed to fix admin password")
        sys.exit(1)