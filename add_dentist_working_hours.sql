-- Add working_hours column to dentists table
-- This column stores working hours for each day of the week as JSONB

-- Add working_hours column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'dentists' 
        AND column_name = 'working_hours'
    ) THEN
        ALTER TABLE dentists ADD COLUMN working_hours JSONB;
        
        -- Create a GIN index for better query performance on JSONB
        CREATE INDEX IF NOT EXISTS idx_dentists_working_hours ON dentists USING GIN (working_hours);
    END IF;
END $$;

-- Update existing dentists with sample working hours
UPDATE dentists 
SET working_hours = '{
  "monday": {"start": "09:00", "end": "17:00"},
  "tuesday": {"start": "09:00", "end": "17:00"},
  "wednesday": {"start": "09:00", "end": "17:00"},
  "thursday": {"start": "09:00", "end": "17:00"},
  "friday": {"start": "09:00", "end": "17:00"}
}'::jsonb
WHERE working_hours IS NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'dentists' 
AND column_name = 'working_hours';

-- Show sample data
SELECT id, name, working_hours 
FROM dentists 
LIMIT 3;
