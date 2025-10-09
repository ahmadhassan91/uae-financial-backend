#!/usr/bin/env python3
"""
Simple admin password fix using direct bcrypt
"""

import os
import sys
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def fix_admin_simple():
    """Fix admin password using direct bcrypt."""
    
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
        # Create engine
        engine = create_engine(database_url)
        
        # Hash password using bcrypt directly
        password = "admin123"
        password_bytes = password.encode('utf-8')
        
        # Ensure password is within bcrypt limits
        if len(password_bytes) > 72:
            print("❌ Password too long for bcrypt")
            return False
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        hashed_str = hashed.decode('utf-8')
        
        print(f"🔐 Generated password hash")
        
        # Update the admin user directly with SQL
        with engine.connect() as conn:
            # Check if admin exists
            result = conn.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": "admin@nationalbonds.ae"}
            )
            admin = result.fetchone()
            
            if admin:
                print(f"📝 Found admin user: {admin.email}")
                
                # Update password
                conn.execute(
                    text("""
                        UPDATE users 
                        SET hashed_password = :password, 
                            is_admin = true, 
                            is_active = true 
                        WHERE email = :email
                    """),
                    {"password": hashed_str, "email": "admin@nationalbonds.ae"}
                )
                conn.commit()
                
                print("✅ Admin password updated successfully!")
                
                # Test the password
                if bcrypt.checkpw(password_bytes, hashed):
                    print("✅ Password verification test passed!")
                else:
                    print("❌ Password verification test failed!")
                    return False
                
                return True
            else:
                print("❌ Admin user not found")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Simple admin password fix...")
    print("=" * 40)
    
    success = fix_admin_simple()
    
    if success:
        print("\n🎉 Admin login fixed!")
        print("Email: admin@nationalbonds.ae")
        print("Password: admin123")
    else:
        print("\n❌ Fix failed")
        sys.exit(1)