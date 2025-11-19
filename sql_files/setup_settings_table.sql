-- Create settings table if it doesn't exist
-- This table stores practice-wide settings (singleton pattern - only one record)
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    practice_name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    working_hours JSONB,
    notifications JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT settings_singleton CHECK (id = 1)
);

-- Create a unique constraint to ensure only one settings record exists
CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_singleton ON settings(id);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_settings_email ON settings(email);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_settings_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_settings_updated_at ON settings;
CREATE TRIGGER update_settings_updated_at
    BEFORE UPDATE ON settings
    FOR EACH ROW
    EXECUTE FUNCTION update_settings_updated_at_column();

-- Insert default settings (optional)
INSERT INTO settings (
    id,
    practice_name,
    address,
    phone,
    email,
    working_hours,
    notifications
) VALUES (
    1,
    'DentalCare Practice',
    '123 Main Street, City, State 12345',
    '(555) 123-4567',
    'info@dentalcare.com',
    '{
        "monday": {"start": "09:00", "end": "17:00", "closed": false},
        "tuesday": {"start": "09:00", "end": "17:00", "closed": false},
        "wednesday": {"start": "09:00", "end": "17:00", "closed": false},
        "thursday": {"start": "09:00", "end": "17:00", "closed": false},
        "friday": {"start": "09:00", "end": "17:00", "closed": false},
        "saturday": {"start": "09:00", "end": "13:00", "closed": false},
        "sunday": {"start": "09:00", "end": "17:00", "closed": true}
    }'::jsonb,
    '{
        "emailReminders": true,
        "smsReminders": true,
        "appointmentConfirmations": true,
        "newPatientAlerts": true
    }'::jsonb
)
ON CONFLICT (id) DO NOTHING;

