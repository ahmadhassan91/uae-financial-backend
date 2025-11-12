#!/usr/bin/env python3
"""Quick test to verify question_variation_mapping column exists."""

from app.database import engine
from sqlalchemy import inspect, text

def test_migration():
    print("🔍 Testing Migration...")
    print("-" * 50)
    
    try:
        # Check if column exists
        inspector = inspect(engine)
        columns = inspector.get_columns('company_trackers')
        
        column_found = False
        for col in columns:
            if col['name'] == 'question_variation_mapping':
                column_found = True
                print(f"✅ Column found: {col['name']}")
                print(f"   Type: {col['type']}")
                print(f"   Nullable: {col['nullable']}")
                break
        
        if not column_found:
            print("❌ ERROR: question_variation_mapping column NOT found!")
            return False
        
        # Test that we can query it
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT id, company_name, question_variation_mapping FROM company_trackers LIMIT 3"
            ))
            rows = result.fetchall()
            print(f"\n✅ Successfully queried {len(rows)} companies")
            for row in rows:
                mapping_status = "Custom" if row[2] else "Default"
                print(f"   - {row[1]}: {mapping_status}")
        
        print("\n" + "=" * 50)
        print("✅ MIGRATION TEST PASSED")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_migration()
    exit(0 if success else 1)
