-- Add new fields to patients table
-- Run this script to add address, emergency_contact, and medical_history columns

-- Add address column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' 
        AND column_name = 'address'
    ) THEN
        ALTER TABLE patients ADD COLUMN address TEXT;
    END IF;
END $$;

-- Add emergency_contact column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' 
        AND column_name = 'emergency_contact'
    ) THEN
        ALTER TABLE patients ADD COLUMN emergency_contact TEXT;
    END IF;
END $$;

-- Add medical_history column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' 
        AND column_name = 'medical_history'
    ) THEN
        ALTER TABLE patients ADD COLUMN medical_history TEXT;
    END IF;
END $$;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'patients' 
ORDER BY ordinal_position;
