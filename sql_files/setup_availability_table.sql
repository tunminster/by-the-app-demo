-- Create availability table if it doesn't exist
CREATE TABLE IF NOT EXISTS availability (
    id SERIAL PRIMARY KEY,
    dentist_id INTEGER NOT NULL REFERENCES dentists(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_slots JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dentist_id, date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_availability_dentist_id ON availability(dentist_id);
CREATE INDEX IF NOT EXISTS idx_availability_date ON availability(date);
CREATE INDEX IF NOT EXISTS idx_availability_dentist_date ON availability(dentist_id, date);
CREATE INDEX IF NOT EXISTS idx_availability_time_slots ON availability USING GIN (time_slots);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_availability_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_availability_updated_at ON availability;
CREATE TRIGGER update_availability_updated_at
    BEFORE UPDATE ON availability
    FOR EACH ROW
    EXECUTE FUNCTION update_availability_updated_at_column();

-- Insert some sample availability data
INSERT INTO availability (dentist_id, date, time_slots) VALUES
(1, '2024-01-15', '[
  {"start": "09:00", "end": "10:00", "available": true},
  {"start": "10:00", "end": "11:00", "available": true},
  {"start": "11:00", "end": "12:00", "available": false},
  {"start": "14:00", "end": "15:00", "available": true},
  {"start": "15:00", "end": "16:00", "available": true},
  {"start": "16:00", "end": "17:00", "available": true}
]'),
(1, '2024-01-16', '[
  {"start": "09:00", "end": "10:00", "available": true},
  {"start": "10:00", "end": "11:00", "available": true},
  {"start": "11:00", "end": "12:00", "available": true},
  {"start": "14:00", "end": "15:00", "available": false},
  {"start": "15:00", "end": "16:00", "available": true},
  {"start": "16:00", "end": "17:00", "available": true}
]'),
(2, '2024-01-15', '[
  {"start": "08:00", "end": "09:00", "available": true},
  {"start": "09:00", "end": "10:00", "available": true},
  {"start": "10:00", "end": "11:00", "available": false},
  {"start": "11:00", "end": "12:00", "available": true},
  {"start": "13:00", "end": "14:00", "available": true},
  {"start": "14:00", "end": "15:00", "available": true}
]'),
(2, '2024-01-17', '[
  {"start": "08:00", "end": "09:00", "available": true},
  {"start": "09:00", "end": "10:00", "available": true},
  {"start": "10:00", "end": "11:00", "available": true},
  {"start": "11:00", "end": "12:00", "available": true},
  {"start": "13:00", "end": "14:00", "available": true},
  {"start": "14:00", "end": "15:00", "available": true}
]'),
(3, '2024-01-15', '[
  {"start": "09:00", "end": "10:00", "available": true},
  {"start": "10:00", "end": "11:00", "available": true},
  {"start": "11:00", "end": "12:00", "available": true},
  {"start": "14:00", "end": "15:00", "available": true},
  {"start": "15:00", "end": "16:00", "available": true}
]'),
(3, '2024-01-18', '[
  {"start": "09:00", "end": "10:00", "available": true},
  {"start": "10:00", "end": "11:00", "available": true},
  {"start": "11:00", "end": "12:00", "available": true},
  {"start": "14:00", "end": "15:00", "available": true},
  {"start": "15:00", "end": "16:00", "available": true}
]')
ON CONFLICT (dentist_id, date) DO NOTHING;

-- Add constraints
ALTER TABLE availability ADD CONSTRAINT chk_availability_date 
    CHECK (date >= CURRENT_DATE);

-- Create a function to validate time slot format
CREATE OR REPLACE FUNCTION validate_time_slots()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if time_slots is a valid JSON array
    IF NOT jsonb_typeof(NEW.time_slots) = 'array' THEN
        RAISE EXCEPTION 'time_slots must be a JSON array';
    END IF;
    
    -- Validate each time slot
    FOR i IN 0..jsonb_array_length(NEW.time_slots) - 1 LOOP
        DECLARE
            slot jsonb := NEW.time_slots->i;
        BEGIN
            -- Check required fields
            IF NOT (slot ? 'start' AND slot ? 'end' AND slot ? 'available') THEN
                RAISE EXCEPTION 'Each time slot must have start, end, and available fields';
            END IF;
            
            -- Check time format (basic validation)
            IF NOT (slot->>'start' ~ '^[0-2][0-9]:[0-5][0-9]$') THEN
                RAISE EXCEPTION 'Invalid start time format. Use HH:MM format';
            END IF;
            
            IF NOT (slot->>'end' ~ '^[0-2][0-9]:[0-5][0-9]$') THEN
                RAISE EXCEPTION 'Invalid end time format. Use HH:MM format';
            END IF;
            
            -- Check that available is boolean
            IF NOT (jsonb_typeof(slot->'available') = 'boolean') THEN
                RAISE EXCEPTION 'Available field must be a boolean';
            END IF;
        END;
    END LOOP;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to validate time slots
DROP TRIGGER IF EXISTS validate_time_slots_trigger ON availability;
CREATE TRIGGER validate_time_slots_trigger
    BEFORE INSERT OR UPDATE ON availability
    FOR EACH ROW
    EXECUTE FUNCTION validate_time_slots();

-- Create a view for easy querying of available slots
CREATE OR REPLACE VIEW available_slots_view AS
SELECT 
    a.id,
    a.dentist_id,
    d.name as dentist_name,
    a.date,
    slot.value as time_slot
FROM availability a
JOIN dentists d ON a.dentist_id = d.id
CROSS JOIN jsonb_array_elements(a.time_slots) as slot
WHERE (slot->>'available')::boolean = true;

-- Create a view for booked slots
CREATE OR REPLACE VIEW booked_slots_view AS
SELECT 
    a.id,
    a.dentist_id,
    d.name as dentist_name,
    a.date,
    slot.value as time_slot
FROM availability a
JOIN dentists d ON a.dentist_id = d.id
CROSS JOIN jsonb_array_elements(a.time_slots) as slot
WHERE (slot->>'available')::boolean = false;
