"""Test script for OTP authentication flow."""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_otp_complete_flow():
    """Test complete OTP authentication flow."""
    
    test_email = "test@example.com"
    
    print("=" * 70)
    print("OTP AUTHENTICATION FLOW TEST")
    print("=" * 70)
    
    # Step 1: Request OTP
    print("\n📧 STEP 1: Requesting OTP...")
    print(f"Email: {test_email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/otp/request",
            json={"email": test_email, "language": "en"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OTP Request Successful!")
            print(f"   Message: {data.get('message')}")
            print(f"   Expires in: {data.get('expires_in')} seconds")
            print(f"\n📬 Check your email ({test_email}) for the OTP code")
        else:
            print(f"❌ OTP Request Failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error requesting OTP: {e}")
        return
    
    # Step 2: Get OTP code from user
    print("\n" + "="* 70)
    print("🔑 STEP 2: Verify OTP")
    print("=" * 70)
    
    # In production, user would enter the code from email
    # For testing, you'll need to get the code from the database or email
    otp_code = input("\nEnter the 6-digit OTP code from email: ").strip()
    
    if not otp_code or len(otp_code) != 6:
        print("❌ Invalid OTP code format")
        return
    
    # Step 3: Verify OTP
    print(f"\n🔍 Verifying OTP: {otp_code}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/otp/verify",
            json={"email": test_email, "code": otp_code}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OTP Verification Successful!")
            print(f"\n👤 User Information:")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Username: {data.get('username')}")
            print(f"   Is New User: {data.get('is_new_user')}")
            print(f"\n🔐 Session Information:")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Expires At: {data.get('expires_at')}")
            print(f"   Survey Count: {data.get('survey_count')}")
            
            # Save session for future use
            session_id = data.get('session_id')
            print(f"\n💾 Session saved! You can use this session_id for authenticated requests:")
            print(f"   {session_id}")
            
        else:
            print(f"❌ OTP Verification Failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error verifying OTP: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✅ OTP AUTHENTICATION TEST COMPLETE!")
    print("=" * 70)


def test_otp_rate_limiting():
    """Test OTP rate limiting (3 requests per 15 minutes)."""
    
    print("\n" + "=" * 70)
    print("TESTING OTP RATE LIMITING")
    print("=" * 70)
    
    test_email = "ratelimit-test@example.com"
    
    for i in range(1, 5):
        print(f"\n📧 Attempt {i}: Requesting OTP...")
        
        response = requests.post(
            f"{BASE_URL}/auth/otp/request",
            json={"email": test_email, "language": "en"}
        )
        
        if response.status_code == 200:
            print(f"   ✅ Request {i} successful")
        elif response.status_code == 429:
            print(f"   ⛔ Rate limit reached!")
            print(f"   Response: {response.json()}")
            break
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
        
        time.sleep(1)  # Small delay between requests


def test_otp_invalid_code():
    """Test OTP verification with invalid code."""
    
    print("\n" + "=" * 70)
    print("TESTING INVALID OTP CODE")
    print("=" * 70)
    
    test_email = "invalid-test@example.com"
    
    # Request OTP first
    print("\n📧 Requesting OTP...")
    response = requests.post(
        f"{BASE_URL}/auth/otp/request",
        json={"email": test_email, "language": "en"}
    )
    
    if response.status_code != 200:
        print("❌ Failed to request OTP")
        return
    
    print("✅ OTP requested successfully")
    
    # Try invalid code
    print("\n🔍 Testing invalid OTP code: 000000")
    response = requests.post(
        f"{BASE_URL}/auth/otp/verify",
        json={"email": test_email, "code": "000000"}
    )
    
    if response.status_code == 400:
        print("✅ Invalid code rejected correctly!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")


def get_otp_from_database():
    """Helper function to get OTP code from database for testing."""
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="uae_financial_health",
            user="clustox1"
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT email, code, expires_at, is_used 
            FROM otp_codes 
            WHERE is_used = false 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("\n📋 Recent OTP Codes from Database:")
            print("-" * 70)
            for row in results:
                email, code, expires_at, is_used = row
                print(f"Email: {email}")
                print(f"Code: {code}")
                print(f"Expires: {expires_at}")
                print(f"Used: {is_used}")
                print("-" * 70)
        else:
            print("\nNo unused OTP codes found in database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error querying database: {e}")
        print("\nYou can manually query the database with:")
        print("SELECT * FROM otp_codes ORDER BY created_at DESC LIMIT 5;")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "rate-limit":
            test_otp_rate_limiting()
        elif test_type == "invalid":
            test_otp_invalid_code()
        elif test_type == "db":
            get_otp_from_database()
        else:
            print("Unknown test type. Use: python test_otp_flow.py [rate-limit|invalid|db]")
    else:
        # Default: Run complete flow test
        test_otp_complete_flow()
        
        print("\n💡 TIP: You can also run specific tests:")
        print("   python test_otp_flow.py rate-limit  # Test rate limiting")
        print("   python test_otp_flow.py invalid     # Test invalid code")
        print("   python test_otp_flow.py db          # View OTP codes from database")
