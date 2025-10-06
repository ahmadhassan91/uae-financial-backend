#!/usr/bin/env python3
"""
Fix admin localization endpoints
"""

import os
import sys
import psycopg2
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_database_query():
    """Test the database query that's failing"""
    print("🔍 Testing Database Query")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        # Test the query that the admin endpoint is using
        print("1. Testing basic query...")
        cursor.execute("""
            SELECT id, content_type, content_id, language, title, text, 
                   options, extra_data, version, is_active, created_at, updated_at
            FROM localized_content 
            WHERE is_active = true
            ORDER BY content_type, content_id, language
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        print(f"✅ Query successful: {len(results)} results")
        
        # Check the data structure
        if results:
            first_row = results[0]
            print(f"✅ First row structure: {len(first_row)} columns")
            print(f"   ID: {first_row[0]}")
            print(f"   Content Type: {first_row[1]}")
            print(f"   Content ID: {first_row[2]}")
            print(f"   Language: {first_row[3]}")
            print(f"   Created At: {first_row[10]} (type: {type(first_row[10])})")
        
        # Test count query
        print("\n2. Testing count query...")
        cursor.execute("SELECT COUNT(*) FROM localized_content WHERE is_active = true")
        count = cursor.fetchone()[0]
        print(f"✅ Count query successful: {count} active items")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database query error: {e}")
        return False

def create_simple_admin_endpoint():
    """Create a simple admin endpoint that works"""
    print(f"\n🔧 Creating Simple Admin Endpoint")
    print("=" * 60)
    
    simple_endpoint_code = '''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from app.models import User, LocalizedContent
from typing import List, Dict, Any

simple_admin_router = APIRouter(prefix="/api/admin/simple", tags=["admin-simple"])

@simple_admin_router.get("/localized-content")
async def get_simple_localized_content(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple endpoint to get localized content without complex schemas."""
    try:
        # Get all localized content
        content_items = db.query(LocalizedContent).filter(
            LocalizedContent.is_active == True
        ).order_by(
            LocalizedContent.content_type,
            LocalizedContent.content_id,
            LocalizedContent.language
        ).limit(100).all()
        
        # Convert to simple dict format
        result = []
        for item in content_items:
            result.append({
                "id": item.id,
                "content_type": item.content_type,
                "content_id": item.content_id,
                "language": item.language,
                "title": item.title,
                "text": item.text[:100] + "..." if item.text and len(item.text) > 100 else item.text,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            })
        
        return {
            "content": result,
            "total": len(result),
            "message": "Simple admin endpoint working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "content": [],
            "total": 0
        }

@simple_admin_router.get("/analytics")
async def get_simple_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple analytics endpoint."""
    try:
        # Get basic counts
        total_content = db.query(LocalizedContent).count()
        english_content = db.query(LocalizedContent).filter(LocalizedContent.language == 'en').count()
        arabic_content = db.query(LocalizedContent).filter(LocalizedContent.language == 'ar').count()
        
        return {
            "total_content_items": total_content,
            "english_items": english_content,
            "arabic_items": arabic_content,
            "translation_coverage": {
                "ar": arabic_content / english_content if english_content > 0 else 0
            },
            "message": "Simple analytics working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_content_items": 0
        }
'''
    
    # Write the simple endpoint
    with open('backend/app/admin/simple_routes.py', 'w') as f:
        f.write(simple_endpoint_code)
    
    print("✅ Created simple admin endpoint at: backend/app/admin/simple_routes.py")
    
    # Update main.py to include the simple router
    main_py_addition = '''
# Add this import at the top with other imports
from app.admin.simple_routes import simple_admin_router

# Add this line with other router includes
app.include_router(simple_admin_router)
'''
    
    print("📝 To enable the simple endpoint, add to main.py:")
    print(main_py_addition)
    
    return True

def test_admin_auth():
    """Test admin authentication"""
    print(f"\n🔐 Testing Admin Authentication")
    print("=" * 60)
    
    try:
        import requests
        
        # Test login
        response = requests.post(
            "http://localhost:8000/auth/login",
            json={"email": "admin@nationalbonds.ae", "password": "admin123"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Admin authentication working")
            
            # Test admin dependency
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Try a simple authenticated endpoint
            test_response = requests.get(
                "http://localhost:8000/api/localization/languages",
                headers=headers
            )
            
            if test_response.status_code == 200:
                print("✅ Token authentication working")
                return True
            else:
                print(f"⚠️  Token test failed: {test_response.status_code}")
                return False
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False

def main():
    """Main function to fix admin endpoints"""
    print("🚀 Fixing Admin Localization Endpoints")
    print("=" * 60)
    
    # Test database query
    db_ok = test_database_query()
    
    # Test admin auth
    auth_ok = test_admin_auth()
    
    # Create simple endpoint
    simple_created = create_simple_admin_endpoint()
    
    print(f"\n" + "=" * 60)
    print("📊 ADMIN ENDPOINT FIX SUMMARY")
    print("=" * 60)
    
    print(f"Database Query: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Admin Auth: {'✅ OK' if auth_ok else '❌ FAILED'}")
    print(f"Simple Endpoint: {'✅ CREATED' if simple_created else '❌ FAILED'}")
    
    if db_ok and auth_ok:
        print(f"\n🎯 NEXT STEPS:")
        print("1. The database and auth are working correctly")
        print("2. The issue is likely in the complex schema validation")
        print("3. Use the simple endpoint for testing: /api/admin/simple/localized-content")
        print("4. Check backend logs for detailed error messages")
        
        print(f"\n🔧 TO FIX THE MAIN ENDPOINT:")
        print("1. Check the datetime serialization in LocalizedContentResponse")
        print("2. Verify all schema fields match the database columns")
        print("3. Add better error handling in the admin routes")
    else:
        print(f"\n❌ FUNDAMENTAL ISSUES:")
        if not db_ok:
            print("- Database connection or query issues")
        if not auth_ok:
            print("- Admin authentication not working")

if __name__ == "__main__":
    main()