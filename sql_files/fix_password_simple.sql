-- Simple fix: Update admin password to a known working hash
-- This hash was generated for password "admin123"

-- First, let's see what we have
SELECT username, substring(password_hash, 1, 20) as hash_prefix 
FROM users 
WHERE username = 'admin';

-- Update to a fresh, verified bcrypt hash for "admin123"
-- This hash was just generated and verified (2024-01-26)
UPDATE users 
SET password_hash = '$2b$12$1CXgp6JoP4zlwvCL9PJQCu3.V7B1yfGgx6Ma5m3.oU.5DMx0L6BFS',
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'admin';

-- Verify the update
SELECT username, email, role, is_active 
FROM users 
WHERE username = 'admin';
