#!/usr/bin/env python3
"""
Fix admin login for PostgreSQL database with clustox1 user
This script will:
1. Connect to PostgreSQL with clustox1 user
2. Create/verify admin user
3. Test login functionality
"""

import os
import sys
import psycopg2
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_postgres_connection():
    """Test PostgreSQL connection with clustox1 user"""
    print("🔄 Testing PostgreSQL connection...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connection successful: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_database_tables():
    """Check if required tables exist"""
    print("🗄️  Checking database tables...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users'
        """)
        
        if cursor.fetchone():
            print("✅ Users table exists")
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"   Columns: {[col[0] for col in columns]}")
            
            # Check if admin user exists
            cursor.execute("SELECT email, is_admin, is_active FROM users WHERE email = %s", 
                         ('admin@nationalbonds.ae',))
            admin_user = cursor.fetchone()
            
            if admin_user:
                print(f"✅ Admin user found: {admin_user[0]}, is_admin: {admin_user[1]}, is_active: {admin_user[2]}")
                cursor.close()
                conn.close()
                return True
            else:
                print("⚠️  Admin user not found")
                cursor.close()
                conn.close()
                return False
        else:
            print("❌ Users table not found")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def create_admin_user():
    """Create admin user in PostgreSQL"""
    print("👤 Creating admin user...")
    
    try:
        # Import after adding to path
        from app.auth.utils import get_password_hash
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = get_password_hash("admin123")
        
        # Check if user exists first
        cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@nationalbonds.ae',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET hashed_password = %s, is_active = %s, is_admin = %s, updated_at = %s
                WHERE email = %s
            """, (
                hashed_password,
                True,
                True,
                datetime.now(),
                'admin@nationalbonds.ae'
            ))
            print("✅ Admin user updated successfully")
        else:
            # Insert new user
            cursor.execute("""
                INSERT INTO users 
                (email, username, hashed_password, is_active, is_admin, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                'admin@nationalbonds.ae',
                'admin',
                hashed_password,
                True,
                True,
                datetime.now(),
                datetime.now()
            ))
            print("✅ Admin user created successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def test_login_api():
    """Test the login API endpoint"""
    print("🔗 Testing login API...")
    
    import requests
    
    try:
        # Test login endpoint
        login_data = {
            "email": "admin@nationalbonds.ae",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   Access token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   Token type: {data.get('token_type', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
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
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ CORS preflight successful")
            print(f"   Allowed methods: {response.headers.get('Access-Control-Allow-Methods', 'N/A')}")
            print(f"   Allowed headers: {response.headers.get('Access-Control-Allow-Headers', 'N/A')}")
            return True
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running")
        return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def run_database_migrations():
    """Run database migrations to ensure tables exist"""
    print("🔄 Running database migrations...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=".",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def main():
    """Main function to fix admin login"""
    print("🚀 PostgreSQL Admin Login Fix Tool")
    print("=" * 50)
    
    # Step 1: Test PostgreSQL connection
    conn_ok = test_postgres_connection()
    if not conn_ok:
        print("\n❌ Cannot connect to PostgreSQL. Please check:")
        print("1. PostgreSQL is running")
        print("2. Database 'uae_financial_health' exists")
        print("3. User 'clustox1' has access")
        return
    
    # Step 2: Run migrations
    migration_ok = run_database_migrations()
    
    # Step 3: Check database tables
    tables_ok = check_database_tables()
    
    # Step 4: Create admin user if needed
    if not tables_ok:
        admin_created = create_admin_user()
    else:
        admin_created = True
    
    # Step 5: Test CORS
    cors_ok = test_cors_preflight()
    
    # Step 6: Test login
    login_ok = test_login_api()
    
    print("\n" + "=" * 50)
    print("📊 POSTGRESQL ADMIN LOGIN FIX SUMMARY")
    print("=" * 50)
    
    print(f"PostgreSQL Connection: {'✅ OK' if conn_ok else '❌ FAILED'}")
    print(f"Database Migrations: {'✅ OK' if migration_ok else '❌ FAILED'}")
    print(f"Database Tables: {'✅ OK' if tables_ok else '❌ FAILED'}")
    print(f"Admin User: {'✅ OK' if admin_created else '❌ FAILED'}")
    print(f"CORS: {'✅ OK' if cors_ok else '❌ FAILED'}")
    print(f"Login API: {'✅ OK' if login_ok else '❌ FAILED'}")
    
    if login_ok:
        print("\n🎉 Admin login is working!")
        print("📋 Credentials:")
        print("   Email: admin@nationalbonds.ae")
        print("   Password: admin123")
        print("\n🌐 Frontend login URL: http://localhost:3000/login")
        print("🔗 Admin dashboard: http://localhost:3000/admin")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        if not conn_ok:
            print("1. Start PostgreSQL: brew services start postgresql")
            print("2. Create database: createdb -U clustox1 uae_financial_health")
        if not migration_ok:
            print("3. Run migrations manually: alembic upgrade head")
        if not cors_ok or not login_ok:
            print("4. Start backend: uvicorn app.main:app --reload")
            print("5. Check backend logs for errors")

if __name__ == "__main__":
    main()