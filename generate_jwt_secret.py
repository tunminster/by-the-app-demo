#!/usr/bin/env python3
"""
Generate a secure JWT_SECRET_KEY for production use.

Usage:
    python generate_jwt_secret.py
"""

import secrets

def generate_jwt_secret():
    """Generate a secure random string for JWT_SECRET_KEY"""
    # Generate 32 bytes of random data (256 bits)
    # token_urlsafe creates a URL-safe base64-encoded string
    secret = secrets.token_urlsafe(32)
    
    print("=" * 70)
    print("JWT_SECRET_KEY Generator")
    print("=" * 70)
    print()
    print("Generated secure JWT_SECRET_KEY:")
    print(f"JWT_SECRET_KEY={secret}")
    print()
    print("Length:", len(secret), "characters")
    print("Entropy:", 32 * 8, "bits (very secure)")
    print()
    print("=" * 70)
    print("Security Notes:")
    print("=" * 70)
    print("✅ This key is cryptographically secure")
    print("✅ Suitable for production use")
    print("✅ Random and unpredictable")
    print()
    print("⚠️  IMPORTANT:")
    print("1. Save this key in a secure location")
    print("2. NEVER commit it to version control")
    print("3. Store it in environment variables or secret management")
    print("4. Use the SAME key across all environments")
    print("=" * 70)
    
    return secret

if __name__ == "__main__":
    generate_jwt_secret()
