#!/usr/bin/env python3
"""
Check actual database records for category_scores structure
"""
import sys
sys.path.append('/Users/clustox_1/Documents/uae-financial-health/backend')

from app.database import SessionLocal
from app.models import FinancialClinicResponse
import json

db = SessionLocal()

print("🔍 Checking Financial Clinic Responses in Database\n")
print("=" * 80)

# Get a few sample responses
responses = db.query(FinancialClinicResponse).limit(5).all()

if not responses:
    print("❌ No responses found in database!")
else:
    print(f"✅ Found {db.query(FinancialClinicResponse).count()} total responses\n")
    
    for idx, response in enumerate(responses, 1):
        print(f"\n📋 Response #{idx} (ID: {response.id})")
        print(f"   Profile ID: {response.profile_id}")
        print(f"   Total Score: {response.total_score}")
        print(f"   Status Band: {response.status_band}")
        print(f"   Created: {response.created_at}")
        
        # Check category_scores structure
        if response.category_scores:
            print(f"\n   📊 Category Scores Type: {type(response.category_scores)}")
            print(f"   📊 Category Scores Content:")
            
            if isinstance(response.category_scores, dict):
                for category, score_data in response.category_scores.items():
                    print(f"      • {category}:")
                    print(f"        Type: {type(score_data)}")
                    print(f"        Value: {score_data}")
                    
                    if isinstance(score_data, dict):
                        print(f"        Keys: {score_data.keys()}")
                        if 'score' in score_data:
                            print(f"        Score value: {score_data['score']}")
            else:
                print(f"      Raw value: {response.category_scores}")
        else:
            print("   ⚠️  No category_scores data")
        
        print("\n   " + "-" * 76)

db.close()
