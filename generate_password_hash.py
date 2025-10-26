#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate hash for "admin123"
password = "admin123"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hashed}")

# Verify it works
verified = pwd_context.verify(password, hashed)
print(f"Verified: {verified}")

# Print SQL update statement
print("\n-- SQL to update:")
print(f"UPDATE users SET password_hash = '{hashed}' WHERE username = 'admin';")
