-- Create patients table if it doesn't exist
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    last_visit DATE,
    next_appointment DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_patients_email ON patients(email);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_patients_status ON patients(status);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_date_of_birth ON patients(date_of_birth);
CREATE INDEX IF NOT EXISTS idx_patients_last_visit ON patients(last_visit);
CREATE INDEX IF NOT EXISTS idx_patients_next_appointment ON patients(next_appointment);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_patients_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_patients_updated_at ON patients;
CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_patients_updated_at_column();

-- Insert some sample patients
INSERT INTO patients (name, email, phone, date_of_birth, last_visit, next_appointment, status) VALUES
('John Smith', 'john.smith@email.com', '(555) 123-4567', '1985-03-15', '2024-01-10', '2024-01-15', 'active'),
('Sarah Johnson', 'sarah.johnson@email.com', '(555) 234-5678', '1990-07-22', '2024-01-05', '2024-01-20', 'active'),
('Michael Brown', 'michael.brown@email.com', '(555) 345-6789', '1978-11-08', '2023-12-15', NULL, 'active'),
('Emily Davis', 'emily.davis@email.com', '(555) 456-7890', '1992-04-30', '2023-11-20', '2024-02-01', 'active'),
('David Wilson', 'david.wilson@email.com', '(555) 567-8901', '1987-09-12', '2023-10-10', NULL, 'inactive'),
('Lisa Anderson', 'lisa.anderson@email.com', '(555) 678-9012', '1995-01-25', '2024-01-08', '2024-01-25', 'active'),
('Robert Taylor', 'robert.taylor@email.com', '(555) 789-0123', '1982-06-18', '2023-09-15', '2024-01-30', 'active'),
('Jennifer Martinez', 'jennifer.martinez@email.com', '(555) 890-1234', '1989-12-03', '2023-08-20', NULL, 'pending'),
('Christopher Lee', 'christopher.lee@email.com', '(555) 901-2345', '1993-02-14', '2024-01-12', '2024-02-10', 'active'),
('Amanda Garcia', 'amanda.garcia@email.com', '(555) 012-3456', '1991-08-07', '2023-07-30', '2024-01-28', 'active')
ON CONFLICT (email) DO NOTHING;

-- Add constraints
ALTER TABLE patients ADD CONSTRAINT chk_patients_status 
    CHECK (status IN ('active', 'inactive', 'pending', 'suspended'));

ALTER TABLE patients ADD CONSTRAINT chk_patients_date_of_birth 
    CHECK (date_of_birth <= CURRENT_DATE);

ALTER TABLE patients ADD CONSTRAINT chk_patients_last_visit 
    CHECK (last_visit IS NULL OR last_visit <= CURRENT_DATE);

ALTER TABLE patients ADD CONSTRAINT chk_patients_next_appointment 
    CHECK (next_appointment IS NULL OR next_appointment >= CURRENT_DATE);
