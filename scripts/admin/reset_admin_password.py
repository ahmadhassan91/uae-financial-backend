#!/usr/bin/env python3
"""
Reset admin user password.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth.utils import get_password_hash

def reset_admin_password():
    """Reset the admin user password."""
    db = SessionLocal()
    
    try:
        # Find the admin user
        admin_user = db.query(User).filter(User.is_admin == True).first()
        
        if not admin_user:
            print("❌ No admin user found")
            return False
        
        print(f"Found admin user: {admin_user.email}")
        
        # Reset password to admin123
        new_password = "admin123"
        hashed_password = get_password_hash(new_password)
        
        admin_user.hashed_password = hashed_password
        db.commit()
        
        print(f"✅ Password reset successfully for {admin_user.email}")
        print(f"   New password: {new_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()