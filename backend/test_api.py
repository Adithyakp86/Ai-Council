"""Simple script to test the authentication API."""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_authentication():
    """Test the authentication flow."""
    
    print("\n🧪 Testing AI Council Authentication API\n")
    
    # 1. Register a new user
    print("1️⃣  Registering new user...")
    register_data = {
        "email": "test@example.com",
        "password": "TestPass123",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response("Register Response", response)
    
    if response.status_code == 201:
        token = response.json().get("token")
        print(f"✅ Registration successful! Token: {token[:50]}...")
    else:
        print("❌ Registration failed!")
        return
    
    # 2. Login with the same user
    print("\n2️⃣  Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "TestPass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Login Response", response)
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"✅ Login successful! Token: {token[:50]}...")
    else:
        print("❌ Login failed!")
        return
    
    # 3. Get current user info
    print("\n3️⃣  Getting current user info...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("Current User Response", response)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ User info retrieved!")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
        print(f"   Role: {user.get('role')}")
    else:
        print("❌ Failed to get user info!")
    
    # 4. Refresh token
    print("\n4️⃣  Refreshing token...")
    response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
    print_response("Refresh Token Response", response)
    
    if response.status_code == 200:
        new_token = response.json().get("token")
        print(f"✅ Token refreshed! New token: {new_token[:50]}...")
    else:
        print("❌ Token refresh failed!")
    
    # 5. Logout
    print("\n5️⃣  Logging out...")
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print_response("Logout Response", response)
    
    if response.status_code == 204:
        print("✅ Logout successful!")
    else:
        print("❌ Logout failed!")
    
    # 6. Test invalid credentials
    print("\n6️⃣  Testing invalid credentials...")
    invalid_login = {
        "email": "test@example.com",
        "password": "WrongPassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=invalid_login)
    print_response("Invalid Login Response", response)
    
    if response.status_code == 401:
        print("✅ Invalid credentials correctly rejected!")
    else:
        print("❌ Invalid credentials should have been rejected!")
    
    print("\n" + "="*60)
    print("🎉 Authentication API Testing Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_authentication()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server!")
        print("   Make sure the backend is running at http://localhost:8000")
        print("   Run: python test_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
