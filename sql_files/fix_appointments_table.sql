-- Add missing timestamp columns to appointments table
-- Run this script to fix the appointments API 500 errors

-- Add created_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE appointments ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        UPDATE appointments SET created_at = NOW() WHERE created_at IS NULL;
    END IF;
END $$;

-- Add updated_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE appointments ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        UPDATE appointments SET updated_at = NOW() WHERE updated_at IS NULL;
    END IF;
END $$;

-- Add status column if it doesn't exist (with default value)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        AND column_name = 'status'
    ) THEN
        ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'confirmed';
        UPDATE appointments SET status = 'confirmed' WHERE status IS NULL;
    END IF;
END $$;

-- Add notes column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        AND column_name = 'notes'
    ) THEN
        ALTER TABLE appointments ADD COLUMN notes TEXT;
    END IF;
END $$;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'appointments' 
ORDER BY ordinal_position;
