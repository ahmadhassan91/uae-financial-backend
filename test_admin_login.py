"""Test admin login functionality."""
import requests
import json

def test_admin_login():
    """Test admin login with the backend API."""
    
    # Backend URL
    base_url = "http://localhost:8000"
    
    # Admin credentials
    admin_credentials = {
        "email": "admin@nationalbonds.ae",
        "password": "admin123"
    }
    
    print("Testing admin login...")
    print(f"Email: {admin_credentials['email']}")
    print(f"Password: {admin_credentials['password']}")
    
    try:
        # Step 1: Login
        print("\n1. Attempting login...")
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=admin_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            print("✅ Login successful!")
            print(f"Access token received: {token_data['access_token'][:50]}...")
            
            # Step 2: Get user info
            print("\n2. Getting user info...")
            user_response = requests.get(
                f"{base_url}/auth/me",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            print(f"User info response status: {user_response.status_code}")
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                print("✅ User info retrieved!")
                print(f"User ID: {user_data['id']}")
                print(f"Email: {user_data['email']}")
                print(f"Username: {user_data['username']}")
                print(f"Is Admin: {user_data['is_admin']}")
                print(f"Is Active: {user_data['is_active']}")
                
                if user_data['is_admin']:
                    print("\n🎉 Admin login test PASSED!")
                    return True
                else:
                    print("\n❌ User is not an admin!")
                    return False
            else:
                print(f"❌ Failed to get user info: {user_response.text}")
                return False
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure the FastAPI server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

def main():
    """Main test function."""
    print("=== Admin Login Test ===")
    
    success = test_admin_login()
    
    if success:
        print("\n✅ Admin login is working correctly!")
        print("You can now use the admin credentials in the frontend:")
        print("- Email: admin@nationalbonds.ae")
        print("- Password: admin123")
    else:
        print("\n❌ Admin login test failed!")
        print("Please check the backend server and admin user setup.")

if __name__ == "__main__":
    main()