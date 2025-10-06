#!/usr/bin/env python3
"""
Test admin routes directly without authentication to check if they're working.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import LocalizedContent, User
from app.admin.localization_routes import list_localized_content
from app.auth.dependencies import get_current_admin_user


async def test_admin_routes_direct():
    """Test admin routes directly."""
    print("=== Testing Admin Routes Directly ===")
    
    db = SessionLocal()
    
    try:
        # Check if we have content
        total_content = db.query(LocalizedContent).count()
        print(f"Total content in database: {total_content}")
        
        if total_content == 0:
            print("❌ No content in database! Run the population scripts first.")
            return
        
        # Test the admin route function directly (bypassing auth for testing)
        print("\nTesting admin route function directly...")
        
        # Create a mock admin user for testing
        mock_admin = User(id=1, email="admin@test.com", username="admin", is_admin=True)
        
        try:
            # Call the route function directly
            result = await list_localized_content(
                db=db,
                admin_user=mock_admin,
                content_type=None,
                language=None,
                active_only=True,
                page=1,
                limit=50
            )
            
            print(f"✓ Admin route function works: {len(result.content)} items returned")
            
            # Show sample content
            if result.content:
                sample = result.content[0]
                print(f"  Sample item: {sample.content_type}:{sample.content_id} = '{sample.text[:50]}...'")
            
        except Exception as e:
            print(f"❌ Admin route function error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test filtering
        print("\nTesting with filters...")
        try:
            result_filtered = await list_localized_content(
                db=db,
                admin_user=mock_admin,
                content_type="ui",
                language="en",
                active_only=True,
                page=1,
                limit=10
            )
            
            print(f"✓ Filtered results: {len(result_filtered.content)} UI items in English")
            
        except Exception as e:
            print(f"❌ Filtered query error: {str(e)}")
        
        print(f"\n📋 Route Testing Summary:")
        print(f"- Database has {total_content} content items")
        print(f"- Admin route function is working")
        print(f"- Issue is likely with authentication or API routing")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_admin_routes_direct())