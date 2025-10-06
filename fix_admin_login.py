#!/usr/bin/env python3
"""
Quick fix for admin login issues
This script will:
1. Switch to SQLite database temporarily
2. Create/verify admin user
3. Test login functionality
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def switch_to_sqlite():
    """Temporarily switch to SQLite database"""
    print("🔄 Switching to SQLite database for testing...")
    
    # Update the .env file to use SQLite
    env_content = """# Database Configuration (SQLite for testing)
DATABASE_URL=sqlite:///./uae_financial_health.db
DATABASE_URL_TEST=sqlite:///./test_uae_financial_health.db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
DEBUG=true

# Email Configuration (for scheduled reports)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# CORS Configuration (defined in config.py)
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Switched to SQLite database")

def check_database():
    """Check if database exists and has users table"""
    db_path = './uae_financial_health.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            print("✅ Users table exists")
            
            # Check if admin user exists
            cursor.execute("SELECT email, is_admin FROM users WHERE email = 'admin@nationalbonds.ae'")
            admin_user = cursor.fetchone()
            
            if admin_user:
                print(f"✅ Admin user found: {admin_user[0]}, is_admin: {admin_user[1]}")
                return True
            else:
                print("⚠️  Admin user not found")
                return False
        else:
            print("❌ Users table not found")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

def create_admin_user():
    """Create admin user directly in SQLite"""
    print("👤 Creating admin user...")
    
    try:
        from app.auth.utils import get_password_hash
        
        conn = sqlite3.connect('./uae_financial_health.db')
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = get_password_hash("admin123")
        
        # Insert or update admin user
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (email, username, hashed_password, is_active, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'admin@nationalbonds.ae',
            'admin',
            hashed_password,
            1,  # is_active
            1,  # is_admin
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Admin user created/updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        conn.close()

def test_login_api():
    """Test the login API endpoint"""
    print("🔗 Testing login API...")
    
    import requests
    import json
    
    try:
        # Test login endpoint
        login_data = {
            "email": "admin@nationalbonds.ae",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   Access token: {data.get('access_token', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running - start with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🌐 Testing CORS preflight...")
    
    import requests
    
    try:
        # Test OPTIONS request (CORS preflight)
        response = requests.options(
            "http://localhost:8000/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        if response.status_code == 200:
            print("✅ CORS preflight successful")
            print(f"   Allowed methods: {response.headers.get('Access-Control-Allow-Methods', 'N/A')}")
            return True
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running")
        return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def main():
    """Main function to fix admin login"""
    print("🚀 Admin Login Fix Tool")
    print("=" * 50)
    
    # Step 1: Switch to SQLite
    switch_to_sqlite()
    
    # Step 2: Check database
    db_ok = check_database()
    
    # Step 3: Create admin user if needed
    if not db_ok:
        create_admin_user()
    
    # Step 4: Test CORS
    cors_ok = test_cors_preflight()
    
    # Step 5: Test login
    login_ok = test_login_api()
    
    print("\n" + "=" * 50)
    print("📊 ADMIN LOGIN FIX SUMMARY")
    print("=" * 50)
    
    print(f"Database: {'✅ OK' if db_ok else '❌ ISSUE'}")
    print(f"CORS: {'✅ OK' if cors_ok else '❌ ISSUE'}")
    print(f"Login: {'✅ OK' if login_ok else '❌ ISSUE'}")
    
    if login_ok:
        print("\n🎉 Admin login is working!")
        print("📋 Credentials:")
        print("   Email: admin@nationalbonds.ae")
        print("   Password: admin123")
        print("\n🌐 Frontend login URL: http://localhost:3000/login")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure backend is running: uvicorn app.main:app --reload")
        print("2. Check if port 8000 is available")
        print("3. Verify database file exists: ./uae_financial_health.db")
        print("4. Check backend logs for errors")
    
    print("\n💡 To revert to PostgreSQL later:")
    print("   Update DATABASE_URL in .env to postgresql://...")

if __name__ == "__main__":
    main()