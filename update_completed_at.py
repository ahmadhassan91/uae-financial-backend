#!/usr/bin/env python3
"""
Script to update existing FinancialClinicResponse records to set completed_at = created_at
Since all existing records are completed, we can backfill this field.
"""
from app.database import SessionLocal
from app.models import FinancialClinicResponse

def update_completed_at():
    """Update all existing responses to have completed_at = created_at"""
    db = SessionLocal()
    try:
        # Get all responses without completed_at
        responses = db.query(FinancialClinicResponse).filter(
            FinancialClinicResponse.completed_at == None
        ).all()
        
        print(f"Found {len(responses)} responses without completed_at")
        
        updated_count = 0
        for response in responses:
            response.completed_at = response.created_at
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"Updated {updated_count} responses...")
                db.commit()
        
        db.commit()
        print(f"✅ Successfully updated {updated_count} responses")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_completed_at()
