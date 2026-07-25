from src.database import init_db
from src.auth import register_user, login_user

def run_test():
    print("--- Starting Authentication System Test ---")
    
    # 1. Initialize DB to make sure we are fresh
    init_db()
    
    test_name = "Sinclaire"
    test_email = "test@student.com"
    test_pass = "secure123"
    
    # 2. Test Registration
    print("\n[Test 1] Registering a new user...")
    success = register_user(test_name, test_email, test_pass)
    if success:
        print("✓ User registered successfully!")
    else:
        print("⚠ Registration failed or user already exists (This is normal if run twice).")
        
    # 3. Test Successful Login
    print("\n[Test 2] Attempting login with CORRECT credentials...")
    user = login_user(test_email, test_pass)
    if user:
        print(f"✓ Login Successful! Welcome back, {user['name']} (ID: {user['user_id']})")
    else:
        print("❌ Login Failed on correct credentials.")
        
    # 4. Test Failed Login
    print("\n[Test 3] Attempting login with WRONG password...")
    failed_user = login_user(test_email, "wrongpassword_abc")
    if not failed_user:
        print("✓ Security System Working: Rejected wrong password perfectly.")
    else:
        print("❌ Security Breach: Allowed entry with a bad password!")

if __name__ == "__main__":
    run_test()