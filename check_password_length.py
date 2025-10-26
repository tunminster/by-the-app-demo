#!/usr/bin/env python3
"""
Check Password Length Issue
This script helps diagnose and fix the bcrypt 72-byte password limitation issue
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_password_length(password):
    """Check password length and provide diagnostics"""
    password_str = str(password)
    password_bytes = len(password_str.encode('utf-8'))
    
    print(f"Password: {password_str[:20]}...")
    print(f"Character count: {len(password_str)}")
    print(f"Byte count: {password_bytes}")
    print(f"Within 72-byte limit: {'✅ Yes' if password_bytes <= 72 else '❌ No'}")
    
    if password_bytes > 72:
        print(f"\n⚠️  This password exceeds the 72-byte bcrypt limit!")
        print(f"Exceeds by: {password_bytes - 72} bytes")
        print("\nSolutions:")
        print("1. If this is an existing user, reset their password")
        print("2. If this is a test account, update the password in the test script")
        print(f"\nSuggested safe password (under 72 bytes): {password_str[:60]}")
    
    return password_bytes <= 72

def test_password_hashing(password):
    """Test if password can be hashed"""
    try:
        password_str = str(password)
        hashed = pwd_context.hash(password_str)
        verified = pwd_context.verify(password_str, hashed)
        print(f"✅ Can hash and verify: {verified}")
        return True
    except Exception as e:
        print(f"❌ Cannot hash password: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Password Length Diagnostics")
    print("=" * 50)
    
    # Check the admin password from the test
    print("\n1️⃣ Checking 'admin123' password:")
    check_password_length("admin123")
    test_password_hashing("admin123")
    
    # Check if there's an actual password that's too long
    print("\n2️⃣ Checking some common test passwords:")
    test_passwords = [
        "admin123",
        "password123",
        "TestPass123!",
        "VeryLongPasswordThatShouldWorkButNeedToCheck12345678901234567890",
        "ExtremelyLongPasswordThatDefinitelyExceeds72BytesBecauseThisIsALongString123456789"
    ]
    
    for pwd in test_passwords:
        print(f"\nTesting: {pwd}")
        is_valid = check_password_length(pwd)
        if is_valid:
            test_password_hashing(pwd)
    
    print("\n" + "=" * 50)
    print("\n💡 Recommendations:")
    print("- Use passwords between 8-60 characters")
    print("- The 'admin' account password may need to be reset")
    print("- Check the database for any passwords exceeding 72 bytes")
    print("\n📝 To fix the admin account:")
    print("1. Connect to your database")
    print("2. Reset the password hash for the admin user")
    print("3. Update the test script with the new password")
