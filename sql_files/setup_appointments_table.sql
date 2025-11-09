-- Create appointments table if it doesn't exist
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    dentist_id INTEGER NOT NULL REFERENCES dentists(id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    treatment VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient);
CREATE INDEX IF NOT EXISTS idx_appointments_dentist_id ON appointments(dentist_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_dentist_date ON appointments(dentist_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_dentist_time ON appointments(dentist_id, appointment_date, appointment_time);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_appointments_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;
CREATE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_appointments_updated_at_column();

-- Insert some sample appointment data
INSERT INTO appointments (patient, phone, dentist_id, appointment_date, appointment_time, treatment, status, notes) VALUES
('John Smith', '(555) 123-4567', 1, '2024-01-15', '09:00', 'Regular Cleaning', 'confirmed', 'Regular checkup and cleaning'),
('Sarah Johnson', '(555) 234-5678', 1, '2024-01-15', '10:00', 'Dental Checkup', 'confirmed', 'Annual dental examination'),
('Michael Brown', '(555) 345-6789', 2, '2024-01-15', '09:00', 'Tooth Extraction', 'confirmed', 'Wisdom tooth removal'),
('Emily Davis', '(555) 456-7890', 1, '2024-01-16', '14:00', 'Crown Placement', 'confirmed', 'Crown installation for molar'),
('David Wilson', '(555) 567-8901', 3, '2024-01-16', '11:00', 'Root Canal', 'confirmed', 'Root canal treatment'),
('Lisa Anderson', '(555) 678-9012', 2, '2024-01-17', '09:00', 'Teeth Whitening', 'confirmed', 'Professional teeth whitening'),
('Robert Taylor', '(555) 789-0123', 1, '2024-01-17', '15:00', 'Dental Filling', 'confirmed', 'Cavity filling'),
('Jennifer Martinez', '(555) 890-1234', 3, '2024-01-18', '10:00', 'Orthodontic Consultation', 'confirmed', 'Braces consultation'),
('Christopher Lee', '(555) 901-2345', 2, '2024-01-18', '14:00', 'Gum Treatment', 'confirmed', 'Periodontal treatment'),
('Amanda Garcia', '(555) 012-3456', 1, '2024-01-19', '11:00', 'Dental Implant', 'confirmed', 'Dental implant procedure')
ON CONFLICT DO NOTHING;

-- Add constraints
ALTER TABLE appointments ADD CONSTRAINT chk_appointments_status 
    CHECK (status IN ('confirmed', 'cancelled', 'completed', 'no_show', 'rescheduled', 'arrived'));

ALTER TABLE appointments ADD CONSTRAINT chk_appointments_date 
    CHECK (appointment_date >= CURRENT_DATE - INTERVAL '1 day');

ALTER TABLE appointments ADD CONSTRAINT chk_appointments_time 
    CHECK (appointment_time >= '08:00' AND appointment_time <= '18:00');

-- Create a unique constraint to prevent double booking
CREATE UNIQUE INDEX IF NOT EXISTS idx_appointments_dentist_datetime 
ON appointments (dentist_id, appointment_date, appointment_time);

-- Create a function to check for appointment conflicts
CREATE OR REPLACE FUNCTION check_appointment_conflict()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if there's already an appointment for this dentist at this time
    IF EXISTS (
        SELECT 1 FROM appointments 
        WHERE dentist_id = NEW.dentist_id 
        AND appointment_date = NEW.appointment_date 
        AND appointment_time = NEW.appointment_time 
        AND id != COALESCE(NEW.id, 0)
    ) THEN
        RAISE EXCEPTION 'Time slot is already booked for this dentist';
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to check for conflicts
DROP TRIGGER IF EXISTS check_appointment_conflict_trigger ON appointments;
CREATE TRIGGER check_appointment_conflict_trigger
    BEFORE INSERT OR UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION check_appointment_conflict();

-- Create views for easy querying
CREATE OR REPLACE VIEW appointments_with_dentist AS
SELECT 
    a.*,
    d.name as dentist_name,
    d.specialty as dentist_specialty
FROM appointments a
JOIN dentists d ON a.dentist_id = d.id;

-- Create view for today's appointments
CREATE OR REPLACE VIEW today_appointments AS
SELECT 
    a.*,
    d.name as dentist_name
FROM appointments a
JOIN dentists d ON a.dentist_id = d.id
WHERE a.appointment_date = CURRENT_DATE
ORDER BY a.appointment_time;

-- Create view for upcoming appointments
CREATE OR REPLACE VIEW upcoming_appointments AS
SELECT 
    a.*,
    d.name as dentist_name
FROM appointments a
JOIN dentists d ON a.dentist_id = d.id
WHERE a.appointment_date >= CURRENT_DATE
ORDER BY a.appointment_date, a.appointment_time;

-- Create view for appointments by status
CREATE OR REPLACE VIEW appointments_by_status AS
SELECT 
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM appointments) as percentage
FROM appointments
GROUP BY status
ORDER BY count DESC;

-- Create a function to get appointment statistics
CREATE OR REPLACE FUNCTION get_appointment_stats()
RETURNS TABLE (
    total_appointments bigint,
    confirmed_appointments bigint,
    cancelled_appointments bigint,
    completed_appointments bigint,
    today_appointments bigint,
    upcoming_appointments bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM appointments) as total_appointments,
        (SELECT COUNT(*) FROM appointments WHERE status = 'confirmed') as confirmed_appointments,
        (SELECT COUNT(*) FROM appointments WHERE status = 'cancelled') as cancelled_appointments,
        (SELECT COUNT(*) FROM appointments WHERE status = 'completed') as completed_appointments,
        (SELECT COUNT(*) FROM appointments WHERE appointment_date = CURRENT_DATE) as today_appointments,
        (SELECT COUNT(*) FROM appointments WHERE appointment_date >= CURRENT_DATE AND appointment_date <= CURRENT_DATE + INTERVAL '7 days') as upcoming_appointments;
END;
$$ language 'plpgsql';

-- Create a function to get dentist appointment statistics
CREATE OR REPLACE FUNCTION get_dentist_appointment_stats(dentist_id_param INTEGER)
RETURNS TABLE (
    dentist_name VARCHAR,
    total_appointments bigint,
    confirmed_appointments bigint,
    completed_appointments bigint,
    upcoming_appointments bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.name as dentist_name,
        (SELECT COUNT(*) FROM appointments WHERE dentist_id = dentist_id_param) as total_appointments,
        (SELECT COUNT(*) FROM appointments WHERE dentist_id = dentist_id_param AND status = 'confirmed') as confirmed_appointments,
        (SELECT COUNT(*) FROM appointments WHERE dentist_id = dentist_id_param AND status = 'completed') as completed_appointments,
        (SELECT COUNT(*) FROM appointments WHERE dentist_id = dentist_id_param AND appointment_date >= CURRENT_DATE) as upcoming_appointments
    FROM dentists d
    WHERE d.id = dentist_id_param;
END;
$$ language 'plpgsql';
