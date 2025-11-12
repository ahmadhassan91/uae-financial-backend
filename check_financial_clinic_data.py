import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from app.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Check Financial Clinic responses
    result = conn.execute(text("SELECT COUNT(*) FROM financial_clinic_responses"))
    count = result.scalar()
    print(f"Total Financial Clinic Responses: {count}")
    
    if count > 0:
        # Get sample data
        result = conn.execute(text("""
            SELECT fcr.id, fcr.total_score, fcr.status_band, fcp.name, fcp.email
            FROM financial_clinic_responses fcr
            JOIN financial_clinic_profiles fcp ON fcr.profile_id = fcp.id
            LIMIT 5
        """))
        
        print("\nSample responses:")
        for row in result:
            print(f"  ID: {row[0]}, Score: {row[1]}, Status: {row[2]}, Name: {row[3]}, Email: {row[4]}")
    else:
        print("\nNo Financial Clinic responses found in database.")
        print("Please submit a Financial Clinic survey first!")

