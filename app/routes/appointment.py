from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, date, time
import jwt
from jwt import PyJWTError
import os
from app.utils.db import conn
from psycopg2.extras import RealDictCursor
import psycopg2

# Initialize router
appointment_router = APIRouter()

# Security setup
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

# Pydantic models
class AppointmentBase(BaseModel):
    patient: str
    phone: str
    dentist_id: int
    appointment_date: date
    appointment_time: str  # Format: "HH:MM"
    treatment: str
    status: str = "confirmed"  # Default status
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient: Optional[str] = None
    phone: Optional[str] = None
    dentist_id: Optional[int] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = None
    treatment: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    dentist_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentSearch(BaseModel):
    patient: Optional[str] = None
    dentist_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[str] = None
    treatment: Optional[str] = None

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
    except PyJWTError:
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
def format_appointment_data(appointment: dict) -> dict:
    """Format appointment data for API response"""
    if appointment:
        # Convert time object to string if needed
        if 'appointment_time' in appointment and appointment['appointment_time']:
            if hasattr(appointment['appointment_time'], 'strftime'):
                appointment['appointment_time'] = appointment['appointment_time'].strftime('%H:%M')
        
        # Ensure all required fields have default values
        appointment.setdefault('status', 'confirmed')
        appointment.setdefault('notes', None)
        appointment.setdefault('created_at', datetime.now(timezone.utc))
        appointment.setdefault('updated_at', datetime.now(timezone.utc))
    
    return appointment

def get_appointment_by_id(appointment_id: int) -> Optional[dict]:
    """Get a single appointment by ID"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM appointments a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.id = %s
        """, (appointment_id,))
        result = cur.fetchone()
        return format_appointment_data(result)

def get_all_appointments() -> List[dict]:
    """Get all appointments"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM appointments a
            JOIN dentists d ON a.dentist_id = d.id
            ORDER BY a.appointment_date, a.appointment_time
        """)
        results = cur.fetchall()
        return [format_appointment_data(appointment) for appointment in results]

def create_appointment(appointment_data: AppointmentCreate) -> dict:
    """Create a new appointment"""
    # Check if dentist exists
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name FROM dentists WHERE id = %s", (appointment_data.dentist_id,))
        dentist = cur.fetchone()
        if not dentist:
            raise HTTPException(status_code=404, detail="Dentist not found")
    
    # Check for time conflicts
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id FROM appointments 
            WHERE dentist_id = %s AND appointment_date = %s AND appointment_time = %s
        """, (appointment_data.dentist_id, appointment_data.date, appointment_data.time))
        conflict = cur.fetchone()
        if conflict:
            raise HTTPException(
                status_code=400,
                detail="Time slot is already booked for this dentist"
            )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO appointments (patient, phone, dentist_id, appointment_date, appointment_time, treatment, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, patient, phone, dentist_id, appointment_date, appointment_time, treatment, status, notes, created_at, updated_at
        """, (
            appointment_data.patient,
            appointment_data.phone,
            appointment_data.dentist_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time,
            appointment_data.treatment,
            appointment_data.status,
            appointment_data.notes
        ))
        result = cur.fetchone()
        result['dentist_name'] = dentist['name']
        return format_appointment_data(result)

def update_appointment(appointment_id: int, appointment_data: AppointmentUpdate) -> Optional[dict]:
    """Update an existing appointment"""
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in appointment_data.dict(exclude_unset=True).items():
        if value is not None:
            # Map Pydantic field names to database column names
            db_field = field
            if field == "appointment_date":
                db_field = "appointment_date"
            elif field == "appointment_time":
                db_field = "appointment_time"
            
            if field == "dentist_id":
                # Check if new dentist exists
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT id, name FROM dentists WHERE id = %s", (value,))
                    dentist = cur.fetchone()
                    if not dentist:
                        raise HTTPException(status_code=404, detail="Dentist not found")
            
            update_fields.append(f"{db_field} = %s")
            values.append(value)
    
    if not update_fields:
        return get_appointment_by_id(appointment_id)
    
    # Check for time conflicts if date/time/dentist is being updated
    if any(field in appointment_data.dict(exclude_unset=True) for field in ['dentist_id', 'appointment_date', 'appointment_time']):
        # Get current appointment data
        current_appointment = get_appointment_by_id(appointment_id)
        if not current_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Use new values or current values
        dentist_id = appointment_data.dentist_id or current_appointment['dentist_id']
        appointment_date = appointment_data.appointment_date or current_appointment['appointment_date']
        appointment_time = appointment_data.appointment_time or current_appointment['appointment_time']
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id FROM appointments 
                WHERE dentist_id = %s AND appointment_date = %s AND appointment_time = %s AND id != %s
            """, (dentist_id, appointment_date, appointment_time, appointment_id))
            conflict = cur.fetchone()
            if conflict:
                raise HTTPException(
                    status_code=400,
                    detail="Time slot is already booked for this dentist"
                )
    
    # Add updated_at timestamp
    update_fields.append("updated_at = %s")
    values.append(datetime.now(timezone.utc))
    
    values.append(appointment_id)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            UPDATE appointments 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, patient, phone, dentist_id, appointment_date, appointment_time, treatment, status, notes, created_at, updated_at
        """, values)
        result = cur.fetchone()
        
        if result:
            # Get dentist name
            with conn.cursor(cursor_factory=RealDictCursor) as dentist_cur:
                dentist_cur.execute("SELECT name FROM dentists WHERE id = %s", (result['dentist_id'],))
                dentist = dentist_cur.fetchone()
                result['dentist_name'] = dentist['name'] if dentist else None
        
        return format_appointment_data(result)

def delete_appointment(appointment_id: int) -> bool:
    """Delete an appointment"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        return cur.rowcount > 0

def search_appointments(
    patient: str = None,
    dentist_id: int = None,
    date_from: date = None,
    date_to: date = None,
    status: str = None,
    treatment: str = None
) -> List[dict]:
    """Search appointments by various criteria"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        conditions = []
        params = []
        
        if patient:
            conditions.append("a.patient ILIKE %s")
            params.append(f"%{patient}%")
        
        if dentist_id:
            conditions.append("a.dentist_id = %s")
            params.append(dentist_id)
        
        if date_from:
            conditions.append("a.appointment_date >= %s")
            params.append(date_from)
        
        if date_to:
            conditions.append("a.appointment_date <= %s")
            params.append(date_to)
        
        if status:
            conditions.append("a.status = %s")
            params.append(status)
        
        if treatment:
            conditions.append("a.treatment ILIKE %s")
            params.append(f"%{treatment}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cur.execute(f"""
            SELECT a.*, d.name as dentist_name
            FROM appointments a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE {where_clause}
            ORDER BY a.appointment_date, a.appointment_time
        """, params)
        results = cur.fetchall()
        return [format_appointment_data(appointment) for appointment in results]

def get_appointments_by_dentist(dentist_id: int, date: date = None) -> List[dict]:
    """Get appointments for a specific dentist"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if date:
            cur.execute("""
                SELECT a.*, d.name as dentist_name
                FROM appointments a
                JOIN dentists d ON a.dentist_id = d.id
                WHERE a.dentist_id = %s AND a.appointment_date = %s
                ORDER BY a.appointment_time
            """, (dentist_id, date))
        else:
            cur.execute("""
                SELECT a.*, d.name as dentist_name
                FROM appointments a
                JOIN dentists d ON a.dentist_id = d.id
                WHERE a.dentist_id = %s
                ORDER BY a.appointment_date, a.appointment_time
            """, (dentist_id,))
        results = cur.fetchall()
        return [format_appointment_data(appointment) for appointment in results]

def get_appointments_by_patient(patient_name: str) -> List[dict]:
    """Get appointments for a specific patient"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM appointments a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.patient ILIKE %s
            ORDER BY a.appointment_date, a.appointment_time
        """, (f"%{patient_name}%",))
        results = cur.fetchall()
        return [format_appointment_data(appointment) for appointment in results]

def update_appointment_status(appointment_id: int, status: str) -> bool:
    """Update appointment status"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE appointments 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """, (status, datetime.now(timezone.utc), appointment_id))
        return cur.rowcount > 0

def get_appointment_statistics() -> dict:
    """Get appointment statistics"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Total appointments
        cur.execute("SELECT COUNT(*) as total FROM appointments")
        total_appointments = cur.fetchone()['total']
        
        # Appointments by status
        cur.execute("""
            SELECT status, COUNT(*) as count 
            FROM appointments 
            GROUP BY status
        """)
        appointments_by_status = cur.fetchall()
        
        # Appointments by dentist
        cur.execute("""
            SELECT d.name as dentist_name, COUNT(a.id) as appointment_count
            FROM dentists d
            LEFT JOIN appointments a ON d.id = a.dentist_id
            GROUP BY d.id, d.name
            ORDER BY appointment_count DESC
        """)
        appointments_by_dentist = cur.fetchall()
        
        # Today's appointments
        cur.execute("""
            SELECT COUNT(*) as today_appointments 
            FROM appointments 
            WHERE appointment_date = CURRENT_DATE
        """)
        today_appointments = cur.fetchone()['today_appointments']
        
        # Upcoming appointments (next 7 days)
        cur.execute("""
            SELECT COUNT(*) as upcoming_appointments 
            FROM appointments 
            WHERE appointment_date >= CURRENT_DATE 
            AND appointment_date <= CURRENT_DATE + INTERVAL '7 days'
        """)
        upcoming_appointments = cur.fetchone()['upcoming_appointments']
        
        # Most common treatments
        cur.execute("""
            SELECT treatment, COUNT(*) as count 
            FROM appointments 
            GROUP BY treatment 
            ORDER BY count DESC 
            LIMIT 5
        """)
        common_treatments = cur.fetchall()
    
    return {
        "total_appointments": total_appointments,
        "appointments_by_status": appointments_by_status,
        "appointments_by_dentist": appointments_by_dentist,
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "common_treatments": common_treatments
    }

# API Endpoints

@appointment_router.get("/appointments", response_model=List[AppointmentResponse])
async def get_appointments(
    patient: Optional[str] = None,
    dentist_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
    treatment: Optional[str] = None,
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get all appointments with optional filtering
    """
    try:
        appointments = search_appointments(patient, dentist_id, date_from, date_to, status, treatment)
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointments: {str(e)}")

@appointment_router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int, current_user: dict = Depends(require_authenticated_user)):
    """
    Get a specific appointment by ID
    """
    try:
        appointment = get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointment: {str(e)}")

@appointment_router.get("/appointments/dentist/{dentist_id}")
async def get_dentist_appointments(
    dentist_id: int,
    date: Optional[date] = None,
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get appointments for a specific dentist
    """
    try:
        appointments = get_appointments_by_dentist(dentist_id, date)
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dentist appointments: {str(e)}")

@appointment_router.get("/appointments/patient/{patient_name}")
async def get_patient_appointments(
    patient_name: str,
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get appointments for a specific patient
    """
    try:
        appointments = get_appointments_by_patient(patient_name)
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch patient appointments: {str(e)}")

@appointment_router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment_endpoint(
    appointment_data: AppointmentCreate, 
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Create a new appointment
    """
    try:
        appointment = create_appointment(appointment_data)
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create appointment: {str(e)}")

@appointment_router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_endpoint(
    appointment_id: int, 
    appointment_data: AppointmentUpdate, 
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Update an existing appointment
    """
    try:
        # Check if appointment exists
        existing_appointment = get_appointment_by_id(appointment_id)
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment = update_appointment(appointment_id, appointment_data)
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update appointment: {str(e)}")

@appointment_router.delete("/appointments/{appointment_id}")
async def delete_appointment_endpoint(
    appointment_id: int, 
    current_user: dict = Depends(require_admin)
):
    """
    Delete an appointment (admin only)
    """
    try:
        # Check if appointment exists
        existing_appointment = get_appointment_by_id(appointment_id)
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        success = delete_appointment(appointment_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete appointment")
        
        return {"message": "Appointment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete appointment: {str(e)}")

@appointment_router.put("/appointments/{appointment_id}/status")
async def update_appointment_status_endpoint(
    appointment_id: int,
    status: str,
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Update appointment status
    """
    try:
        # Check if appointment exists
        existing_appointment = get_appointment_by_id(appointment_id)
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        success = update_appointment_status(appointment_id, status)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update appointment status")
        
        return {"message": "Appointment status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update appointment status: {str(e)}")

@appointment_router.get("/appointments/stats")
async def get_appointment_stats(current_user: dict = Depends(require_admin)):
    """
    Get appointment statistics (admin only)
    """
    try:
        stats = get_appointment_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointment statistics: {str(e)}")

@appointment_router.get("/appointments/statuses")
async def get_appointment_statuses(current_user: dict = Depends(require_authenticated_user)):
    """
    Get all available appointment statuses
    """
    return {
        "statuses": ["confirmed", "cancelled", "completed", "no_show", "rescheduled"],
        "descriptions": {
            "confirmed": "Appointment is confirmed",
            "cancelled": "Appointment is cancelled",
            "completed": "Appointment is completed",
            "no_show": "Patient did not show up",
            "rescheduled": "Appointment is rescheduled"
        }
    }
