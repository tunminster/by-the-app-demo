# Patient Entity - New Fields Added

## Overview

Added three new optional fields to the Patient entity to enhance patient information management:

- **address** - Patient's home address
- **emergency_contact** - Emergency contact information  
- **medical_history** - Patient's medical history and notes

## New Fields

### Address
- **Type:** `Optional[str]`
- **Default:** `None`
- **Purpose:** Store patient's complete home address
- **Example:** `"123 Main St, Anytown, ST 12345"`

### Emergency Contact
- **Type:** `Optional[str]`
- **Default:** `None`
- **Purpose:** Store emergency contact information
- **Example:** `"Jane Doe - (555) 987-6543"`

### Medical History
- **Type:** `Optional[str]`
- **Default:** `None`
- **Purpose:** Store patient's medical history, allergies, and notes
- **Example:** `"Allergic to penicillin. Previous root canal in 2020."`

## Updated Models

### PatientBase
```python
class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    address: Optional[str] = None                    # NEW
    emergency_contact: Optional[str] = None          # NEW
    medical_history: Optional[str] = None            # NEW
    status: str = "active"
```

### PatientCreate
```python
class PatientCreate(PatientBase):
    pass  # Inherits all fields including new ones
```

### PatientUpdate
```python
class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None                    # NEW
    emergency_contact: Optional[str] = None          # NEW
    medical_history: Optional[str] = None            # NEW
    status: Optional[str] = None
```

### PatientResponse
```python
class PatientResponse(PatientBase):
    id: int
    last_visit: Optional[date] = None
    next_appointment: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    # Includes all new fields from PatientBase
```

## API Endpoints

All existing patient endpoints now support the new fields:

### Create Patient
**POST** `/api/patients`

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "(555) 123-4567",
  "date_of_birth": "1990-05-15",
  "address": "123 Main St, Anytown, ST 12345",
  "emergency_contact": "Jane Doe - (555) 987-6543",
  "medical_history": "Allergic to penicillin. Previous root canal in 2020.",
  "status": "active"
}
```

### Update Patient
**PUT** `/api/patients/{id}`

```json
{
  "address": "456 Oak Ave, Newtown, ST 67890",
  "emergency_contact": "Bob Smith - (555) 111-2222",
  "medical_history": "Updated: Allergic to penicillin and latex. Previous root canal in 2020, cleaning in 2023."
}
```

### Get Patient
**GET** `/api/patients/{id}`

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "(555) 123-4567",
  "date_of_birth": "1990-05-15",
  "address": "123 Main St, Anytown, ST 12345",
  "emergency_contact": "Jane Doe - (555) 987-6543",
  "medical_history": "Allergic to penicillin. Previous root canal in 2020.",
  "status": "active",
  "last_visit": null,
  "next_appointment": null,
  "created_at": "2025-10-26T10:30:00Z",
  "updated_at": "2025-10-26T10:30:00Z"
}
```

## Database Migration

Run the migration script to add the new columns to your database:

```bash
psql -h your_host -U your_user -d your_database -f add_patient_fields.sql
```

### Manual SQL Commands

```sql
-- Add address column
ALTER TABLE patients ADD COLUMN address TEXT;

-- Add emergency_contact column  
ALTER TABLE patients ADD COLUMN emergency_contact TEXT;

-- Add medical_history column
ALTER TABLE patients ADD COLUMN medical_history TEXT;
```

## Frontend Usage

### JavaScript Example

```javascript
// Create patient with new fields
const newPatient = {
  name: "John Doe",
  email: "john.doe@example.com", 
  phone: "(555) 123-4567",
  date_of_birth: "1990-05-15",
  address: "123 Main St, Anytown, ST 12345",
  emergency_contact: "Jane Doe - (555) 987-6543",
  medical_history: "Allergic to penicillin. Previous root canal in 2020.",
  status: "active"
};

const response = await fetch('/api/patients', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(newPatient)
});

const patient = await response.json();
console.log('Created patient:', patient);
```

### React Form Example

```jsx
import React, { useState } from 'react';

const PatientForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    address: '',
    emergency_contact: '',
    medical_history: '',
    status: 'active'
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Name:</label>
        <input 
          name="name" 
          value={formData.name} 
          onChange={handleChange} 
          required 
        />
      </div>
      
      <div>
        <label>Email:</label>
        <input 
          name="email" 
          type="email" 
          value={formData.email} 
          onChange={handleChange} 
          required 
        />
      </div>
      
      <div>
        <label>Phone:</label>
        <input 
          name="phone" 
          value={formData.phone} 
          onChange={handleChange} 
          required 
        />
      </div>
      
      <div>
        <label>Date of Birth:</label>
        <input 
          name="date_of_birth" 
          type="date" 
          value={formData.date_of_birth} 
          onChange={handleChange} 
          required 
        />
      </div>
      
      <div>
        <label>Address:</label>
        <textarea 
          name="address" 
          value={formData.address} 
          onChange={handleChange}
          rows="3"
        />
      </div>
      
      <div>
        <label>Emergency Contact:</label>
        <input 
          name="emergency_contact" 
          value={formData.emergency_contact} 
          onChange={handleChange}
        />
      </div>
      
      <div>
        <label>Medical History:</label>
        <textarea 
          name="medical_history" 
          value={formData.medical_history} 
          onChange={handleChange}
          rows="4"
        />
      </div>
      
      <button type="submit">Create Patient</button>
    </form>
  );
};
```

## Testing

Run the test script to verify the new fields work correctly:

```bash
python test_patient_new_fields.py
```

This will test:
1. ✅ Creating patients with new fields
2. ✅ Getting all patients (includes new fields)
3. ✅ Getting specific patient (includes new fields)
4. ✅ Updating patient with new fields
5. ✅ Searching patients

## Benefits

1. **Enhanced Patient Records** - More comprehensive patient information
2. **Better Emergency Handling** - Quick access to emergency contacts
3. **Medical History Tracking** - Store important medical information
4. **Address Management** - Complete address information for mailings
5. **Backward Compatible** - All fields are optional, existing data unaffected

## Notes

- All new fields are **optional** - existing patients will have `null` values
- Fields can be **updated independently** - you can update just address without affecting other fields
- **Text fields** can store long content (medical history, full addresses)
- **Database queries** automatically include the new fields
- **API responses** include all fields for complete patient information
