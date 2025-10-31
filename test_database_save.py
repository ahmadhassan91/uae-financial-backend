"""Test Financial Clinic Database Save Functionality"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("\n🧪 Testing Financial Clinic Database Save")
print("=" * 60)

# Sample profile data
profile_data = {
    "name": "Ahmad Hassan",
    "date_of_birth": "29/02/1991",
    "gender": "Male",
    "nationality": "Emirati",
    "emirate": "Dubai",
    "employment_status": "Self-Employed",
    "income_range": "Below 5K",
    "email": "ahmad.hassan.test@clustox.com",
    "mobile_number": "+972542865966",
    "children": 0
}

# Sample answers (use integers 1-5 for all questions)
answers = {
    "fc_q1": 3,
    "fc_q2": 1,
    "fc_q3": 2,
    "fc_q4": 4,
    "fc_q5": 2,
    "fc_q6": 5,
    "fc_q7": 1,
    "fc_q8": 4,
    "fc_q9": 3,
    "fc_q10": 2,
    "fc_q11": 5,
    "fc_q12": 1,
    "fc_q13": 2,
    "fc_q14": 3,
    "fc_q15": 4,
    "fc_q16": 2
}

# Test 1: Submit survey and save to database
print("\n1. Submitting survey...")
try:
    response = requests.post(
        f"{BASE_URL}/financial-clinic/submit",
        json={
            "profile": profile_data,
            "answers": answers
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Survey submitted successfully!")
        print(f"      Survey Response ID: {data.get('survey_response_id')}")
        print(f"      Total Score: {data.get('total_score')}")
        print(f"      Status Band: {data.get('status_band')}")
        print(f"      Saved At: {data.get('saved_at')}")
        
        # Store for next test
        survey_response_id = data.get('survey_response_id')
        
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"      {response.text}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Generate PDF from saved response
if survey_response_id:
    print(f"\n2. Generating PDF from saved response (ID: {survey_response_id})...")
    try:
        response = requests.post(
            f"{BASE_URL}/financial-clinic/report/pdf",
            json={
                "survey_response_id": survey_response_id,
                "language": "en"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Check if it's a PDF or JSON error
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/pdf' in content_type:
                pdf_size = len(response.content)
                print(f"   ✅ PDF generated from database ({pdf_size} bytes)")
                
                # Save PDF
                with open('/tmp/test_from_database.pdf', 'wb') as f:
                    f.write(response.content)
                print(f"   📄 Saved to: /tmp/test_from_database.pdf")
            else:
                # JSON response (might be error or placeholder)
                data = response.json()
                print(f"   ⚠️  Response: {data}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"      {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Test 3: Submit same profile again (should update, not create duplicate)
print("\n3. Submitting again with same email (should update profile)...")
try:
    # Different answers but same email
    different_answers = answers.copy()
    different_answers['fc_q1'] = 2  # Use integer instead of 'irregular'
    different_answers['fc_q5'] = 4  # Use integer instead of 'yes'
    
    response = requests.post(
        f"{BASE_URL}/financial-clinic/submit",
        json={
            "profile": profile_data,
            "answers": different_answers
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Second submission successful!")
        print(f"      New Survey Response ID: {data.get('survey_response_id')}")
        print(f"      Total Score: {data.get('total_score')}")
        print(f"      Status Band: {data.get('status_band')}")
        print(f"      (Profile should be updated, not duplicated)")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Database Save Tests Complete!")
print("\nNext: Check database to verify:")
print("- Profile was created/updated")
print("- Survey responses were saved")
print("- No duplicate profiles exist")
print("\n")
