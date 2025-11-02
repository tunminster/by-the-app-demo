-- Create dentists table if it doesn't exist
CREATE TABLE IF NOT EXISTS dentists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    license VARCHAR(100) UNIQUE NOT NULL,
    years_of_experience INTEGER NOT NULL CHECK (years_of_experience >= 0),
    working_days VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on specialty for faster searches
CREATE INDEX IF NOT EXISTS idx_dentists_specialty ON dentists(specialty);

-- Create an index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_dentists_email ON dentists(email);

-- Insert some sample data (optional)
INSERT INTO dentists (name, specialty, email, phone, license, years_of_experience, working_days) VALUES
('Dr. Sarah Nguyen', 'General Dentistry', 'sarah.nguyen@dentalclinic.com', '+1-555-0101', 'DDS-001', 8, '5 days/week'),
('Dr. Michael Chen', 'Orthodontics', 'michael.chen@dentalclinic.com', '+1-555-0102', 'DDS-002', 12, '5 days/week'),
('Dr. Emily Rodriguez', 'Oral Surgery', 'emily.rodriguez@dentalclinic.com', '+1-555-0103', 'DDS-003', 15, '4 days/week'),
('Dr. James Wilson', 'Periodontics', 'james.wilson@dentalclinic.com', '+1-555-0104', 'DDS-004', 10, '5 days/week'),
('Dr. Lisa Park', 'Pediatric Dentistry', 'lisa.park@dentalclinic.com', '+1-555-0105', 'DDS-005', 6, '5 days/week')
ON CONFLICT (email) DO NOTHING;
