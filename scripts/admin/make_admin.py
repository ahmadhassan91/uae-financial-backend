#!/usr/bin/env python3
"""
Make a user an admin.
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import User
from app.config import settings

def make_user_admin(email: str):
    """Make a user an admin."""
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email {email} not found")
            return False
        
        # Make user admin
        user.is_admin = True
        db.commit()
        
        print(f"✅ User {email} is now an admin")
        return True
        
    except Exception as e:
        print(f"❌ Error making user admin: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    email = "admin@nationalbonds.ae"
    make_user_admin(email)