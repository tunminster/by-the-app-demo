from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone, date
from jose import JWTError, jwt
import os
from app.utils.db import conn
from psycopg2.extras import RealDictCursor
import psycopg2

# Initialize router
patient_router = APIRouter()

# Security setup
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

# Pydantic models
class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    status: str = "active"  # Default status

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    status: Optional[str] = None

class PatientResponse(PatientBase):
    id: int
    last_visit: Optional[date] = None
    next_appointment: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PatientSearch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    date_of_birth_from: Optional[date] = None
    date_of_birth_to: Optional[date] = None

# Authentication functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
    
    if user is None:
        raise credentials_exception
    
    if not user.get('is_active', False):
        raise HTTPException(
            status_code=401,
            detail="Inactive user"
        )
    
    return user

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role"""
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return current_user

def require_admin_or_receptionist(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin or receptionist role"""
    if current_user.get('role') not in ['admin', 'receptionist']:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return current_user

def require_authenticated_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Require any authenticated user"""
    return current_user

# Database helper functions
def get_patient_by_id(patient_id: int) -> Optional[dict]:
    """Get a single patient by ID"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        return cur.fetchone()

def get_patient_by_email(email: str) -> Optional[dict]:
    """Get a patient by email"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM patients WHERE email = %s", (email,))
        return cur.fetchone()

def get_all_patients() -> List[dict]:
    """Get all patients"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, email, phone, date_of_birth, last_visit, 
                   next_appointment, status, created_at, updated_at 
            FROM patients 
            ORDER BY created_at DESC
        """)
        return cur.fetchall()

def create_patient(patient_data: PatientCreate) -> dict:
    """Create a new patient"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO patients (name, email, phone, date_of_birth, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, email, phone, date_of_birth, last_visit, 
                      next_appointment, status, created_at, updated_at
        """, (
            patient_data.name,
            patient_data.email,
            patient_data.phone,
            patient_data.date_of_birth,
            patient_data.status
        ))
        return cur.fetchone()

def update_patient(patient_id: int, patient_data: PatientUpdate) -> Optional[dict]:
    """Update an existing patient"""
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in patient_data.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            values.append(value)
    
    if not update_fields:
        return get_patient_by_id(patient_id)
    
    # Add updated_at timestamp
    update_fields.append("updated_at = %s")
    values.append(datetime.now(timezone.utc))
    
    values.append(patient_id)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            UPDATE patients 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, email, phone, date_of_birth, last_visit, 
                      next_appointment, status, created_at, updated_at
        """, values)
        return cur.fetchone()

def delete_patient(patient_id: int) -> bool:
    """Delete a patient (soft delete by setting status to 'inactive')"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE patients 
            SET status = 'inactive', updated_at = %s
            WHERE id = %s
        """, (datetime.now(timezone.utc), patient_id))
        return cur.rowcount > 0

def search_patients(
    name: str = None,
    email: str = None,
    phone: str = None,
    status: str = None,
    date_of_birth_from: date = None,
    date_of_birth_to: date = None
) -> List[dict]:
    """Search patients by various criteria"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        conditions = []
        params = []
        
        if name:
            conditions.append("name ILIKE %s")
            params.append(f"%{name}%")
        
        if email:
            conditions.append("email ILIKE %s")
            params.append(f"%{email}%")
        
        if phone:
            conditions.append("phone ILIKE %s")
            params.append(f"%{phone}%")
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if date_of_birth_from:
            conditions.append("date_of_birth >= %s")
            params.append(date_of_birth_from)
        
        if date_of_birth_to:
            conditions.append("date_of_birth <= %s")
            params.append(date_of_birth_to)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cur.execute(f"""
            SELECT id, name, email, phone, date_of_birth, last_visit, 
                   next_appointment, status, created_at, updated_at
            FROM patients 
            WHERE {where_clause}
            ORDER BY created_at DESC
        """, params)
        return cur.fetchall()

def update_patient_last_visit(patient_id: int, visit_date: date):
    """Update patient's last visit date"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE patients 
            SET last_visit = %s, updated_at = %s
            WHERE id = %s
        """, (visit_date, datetime.now(timezone.utc), patient_id))

def update_patient_next_appointment(patient_id: int, appointment_date: date):
    """Update patient's next appointment date"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE patients 
            SET next_appointment = %s, updated_at = %s
            WHERE id = %s
        """, (appointment_date, datetime.now(timezone.utc), patient_id))

def get_patient_appointments(patient_id: int) -> List[dict]:
    """Get all appointments for a specific patient"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM appointments a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.patient_name = (
                SELECT name FROM patients WHERE id = %s
            )
            ORDER BY a.appointment_date, a.appointment_time
        """, (patient_id,))
        return cur.fetchall()

def get_patient_statistics() -> dict:
    """Get patient statistics"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Total patients
        cur.execute("SELECT COUNT(*) as total FROM patients")
        total_patients = cur.fetchone()['total']
        
        # Active patients
        cur.execute("SELECT COUNT(*) as active FROM patients WHERE status = 'active'")
        active_patients = cur.fetchone()['active']
        
        # Patients by status
        cur.execute("""
            SELECT status, COUNT(*) as count 
            FROM patients 
            GROUP BY status
        """)
        patients_by_status = cur.fetchall()
        
        # Recent patients (last 30 days)
        cur.execute("""
            SELECT COUNT(*) as recent_patients 
            FROM patients 
            WHERE created_at >= NOW() - INTERVAL '30 days'
        """)
        recent_patients = cur.fetchone()['recent_patients']
        
        # Patients with upcoming appointments
        cur.execute("""
            SELECT COUNT(*) as upcoming_appointments 
            FROM patients 
            WHERE next_appointment >= CURRENT_DATE
        """)
        upcoming_appointments = cur.fetchone()['upcoming_appointments']
    
    return {
        "total_patients": total_patients,
        "active_patients": active_patients,
        "inactive_patients": total_patients - active_patients,
        "patients_by_status": patients_by_status,
        "recent_patients": recent_patients,
        "upcoming_appointments": upcoming_appointments
    }

# API Endpoints

@patient_router.get("/patients", response_model=List[PatientResponse])
async def get_patients(
    search: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get all patients with optional search and status filtering
    """
    try:
        if search:
            patients = search_patients(name=search, email=search, phone=search)
        else:
            patients = search_patients(status=status)
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch patients: {str(e)}")

@patient_router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, current_user: dict = Depends(require_authenticated_user)):
    """
    Get a specific patient by ID
    """
    try:
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch patient: {str(e)}")

@patient_router.post("/patients", response_model=PatientResponse)
async def create_patient_endpoint(patient_data: PatientCreate, current_user: dict = Depends(require_admin_or_receptionist)):
    """
    Create a new patient
    """
    try:
        # Check if patient with same email already exists
        existing_patient = get_patient_by_email(patient_data.email)
        if existing_patient:
            raise HTTPException(status_code=400, detail="Patient with this email already exists")
        
        patient = create_patient(patient_data)
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")

@patient_router.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient_endpoint(patient_id: int, patient_data: PatientUpdate, current_user: dict = Depends(require_admin_or_receptionist)):
    """
    Update an existing patient
    """
    try:
        # Check if patient exists
        existing_patient = get_patient_by_id(patient_id)
        if not existing_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Check for email conflicts if email is being updated
        if patient_data.email:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id FROM patients 
                    WHERE email = %s AND id != %s
                """, (patient_data.email, patient_id))
                conflict = cur.fetchone()
                if conflict:
                    raise HTTPException(
                        status_code=400,
                        detail="Another patient with this email already exists"
                    )
        
        patient = update_patient(patient_id, patient_data)
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update patient: {str(e)}")

@patient_router.delete("/patients/{patient_id}")
async def delete_patient_endpoint(patient_id: int, current_user: dict = Depends(require_admin)):
    """
    Deactivate a patient (admin only)
    """
    try:
        # Check if patient exists
        existing_patient = get_patient_by_id(patient_id)
        if not existing_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        success = delete_patient(patient_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to deactivate patient")
        
        return {"message": "Patient deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate patient: {str(e)}")

@patient_router.get("/patients/{patient_id}/appointments")
async def get_patient_appointments_endpoint(patient_id: int, current_user: dict = Depends(require_authenticated_user)):
    """
    Get all appointments for a specific patient
    """
    try:
        # Check if patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        appointments = get_patient_appointments(patient_id)
        return appointments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch patient appointments: {str(e)}")

@patient_router.put("/patients/{patient_id}/last-visit")
async def update_last_visit(patient_id: int, visit_date: date, current_user: dict = Depends(require_admin_or_receptionist)):
    """
    Update patient's last visit date
    """
    try:
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        update_patient_last_visit(patient_id, visit_date)
        return {"message": "Last visit updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update last visit: {str(e)}")

@patient_router.put("/patients/{patient_id}/next-appointment")
async def update_next_appointment(patient_id: int, appointment_date: date, current_user: dict = Depends(require_admin_or_receptionist)):
    """
    Update patient's next appointment date
    """
    try:
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        update_patient_next_appointment(patient_id, appointment_date)
        return {"message": "Next appointment updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update next appointment: {str(e)}")

@patient_router.get("/patients/stats")
async def get_patient_stats(current_user: dict = Depends(require_admin)):
    """
    Get patient statistics (admin only)
    """
    try:
        stats = get_patient_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch patient statistics: {str(e)}")

@patient_router.get("/patients/statuses")
async def get_patient_statuses(current_user: dict = Depends(require_authenticated_user)):
    """
    Get all available patient statuses
    """
    return {
        "statuses": ["active", "inactive", "pending", "suspended"],
        "descriptions": {
            "active": "Patient is active and can book appointments",
            "inactive": "Patient is inactive",
            "pending": "Patient registration pending",
            "suspended": "Patient account suspended"
        }
    }
