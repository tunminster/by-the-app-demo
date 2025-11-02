-- Fix the admin password hash
-- This updates the password_hash for the admin user to a valid bcrypt hash for "admin123"
-- Generated on: 2024-01-26

-- Update admin password
UPDATE users 
SET password_hash = '$2b$12$E0Xl3jlBPzVVUCtQCkXAMu7tU13nzc3aQ7kGtXYtFAcgcyNF5Q/4S',
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'admin';

-- Verify the update
SELECT username, email, role, is_active, updated_at 
FROM users 
WHERE username = 'admin';
