from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime, timezone
import jwt
from jwt import PyJWTError
import os
from app.utils.db import conn
from psycopg2.extras import RealDictCursor
import psycopg2

# Initialize router
dentist_router = APIRouter()

# Security setup
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

# Pydantic models for request/response
class WorkingHours(BaseModel):
    """Working hours for a single day"""
    start: str  # Format: "HH:MM"
    end: str    # Format: "HH:MM"

class DentistBase(BaseModel):
    name: str
    specialty: str
    email: EmailStr
    phone: str
    license: str
    years_of_experience: int
    working_days: str  # e.g., "5 days/week"
    working_hours: Dict[str, WorkingHours]  # Day -> Working Hours

class DentistCreate(DentistBase):
    pass

class DentistUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license: Optional[str] = None
    years_of_experience: Optional[int] = None
    working_days: Optional[str] = None
    working_hours: Optional[Dict[str, WorkingHours]] = None

class DentistResponse(DentistBase):
    id: int
    
    class Config:
        from_attributes = True

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

def require_admin_or_dentist(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin or dentist role"""
    if current_user.get('role') not in ['admin', 'dentist']:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return current_user

# Database helper functions
def get_dentist_by_id(dentist_id: int) -> Optional[dict]:
    """Get a single dentist by ID"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM dentists WHERE id = %s", (dentist_id,))
        result = cur.fetchone()
        
        # working_hours is already a dict from psycopg2 JSONB
        # No need to parse it
        
        return result

def get_all_dentists() -> List[dict]:
    """Get all dentists"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM dentists ORDER BY name")
        results = cur.fetchall()
        
        # working_hours is already a dict from psycopg2 JSONB
        # No need to parse it
        
        return results

def create_dentist(dentist_data: DentistCreate) -> dict:
    """Create a new dentist"""
    # Convert working_hours to JSON string
    working_hours_json = None
    if dentist_data.working_hours:
        # Convert entries to plain dicts (supports both Pydantic models and plain dicts)
        working_hours_dict = {}
        for day, hours in dentist_data.working_hours.items():
            if hasattr(hours, "dict"):
                working_hours_dict[day] = hours.dict()
            else:
                working_hours_dict[day] = hours
        import json
        working_hours_json = json.dumps(working_hours_dict)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO dentists (name, specialty, email, phone, license, years_of_experience, working_days, working_hours)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING *
        """, (
            dentist_data.name,
            dentist_data.specialty,
            dentist_data.email,
            dentist_data.phone,
            dentist_data.license,
            dentist_data.years_of_experience,
            dentist_data.working_days,
            working_hours_json
        ))
        result = cur.fetchone()
        
        # working_hours is already a dict from psycopg2 JSONB
        # No need to parse it
        
        return result

def update_dentist(dentist_id: int, dentist_data: DentistUpdate) -> Optional[dict]:
    """Update an existing dentist"""
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in dentist_data.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            values.append(value)
    
    if not update_fields:
        return get_dentist_by_id(dentist_id)
    
def update_dentist(dentist_id: int, dentist_data: DentistUpdate) -> Optional[dict]:
    """Update an existing dentist"""
    import json
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in dentist_data.dict(exclude_unset=True).items():
        if value is not None:
            # Handle working_hours specially
            if field == 'working_hours':
                # Convert entries to plain dicts (supports both Pydantic models and plain dicts)
                working_hours_dict = {}
                for day, hours in value.items():
                    if hasattr(hours, "dict"):
                        working_hours_dict[day] = hours.dict()
                    else:
                        working_hours_dict[day] = hours
                values.append(json.dumps(working_hours_dict))
                update_fields.append(f"{field} = %s::jsonb")
            else:
                values.append(value)
                update_fields.append(f"{field} = %s")
    
    if not update_fields:
        return get_dentist_by_id(dentist_id)
    
    values.append(dentist_id)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            UPDATE dentists 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """, values)
        result = cur.fetchone()
        
        # working_hours is already a dict from psycopg2 JSONB
        # No need to parse it
        
        return result

def delete_dentist(dentist_id: int) -> bool:
    """Delete a dentist"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM dentists WHERE id = %s", (dentist_id,))
        return cur.rowcount > 0

def search_dentists(query: str = None, specialty: str = None) -> List[dict]:
    """Search dentists by name or specialty"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if query and specialty:
            cur.execute("""
                SELECT * FROM dentists 
                WHERE (name ILIKE %s OR specialty ILIKE %s) AND specialty ILIKE %s
                ORDER BY name
            """, (f"%{query}%", f"%{query}%", f"%{specialty}%"))
        elif query:
            cur.execute("""
                SELECT * FROM dentists 
                WHERE name ILIKE %s OR specialty ILIKE %s
                ORDER BY name
            """, (f"%{query}%", f"%{query}%"))
        elif specialty:
            cur.execute("""
                SELECT * FROM dentists 
                WHERE specialty ILIKE %s
                ORDER BY name
            """, (f"%{specialty}%",))
        else:
            return get_all_dentists()
        return cur.fetchall()

# API Endpoints

@dentist_router.get("/dentists", response_model=List[DentistResponse])
async def get_dentists(
    search: Optional[str] = None,
    specialty: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all dentists with optional search and specialty filtering
    """
    try:
        dentists = search_dentists(search, specialty)
        return dentists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dentists: {str(e)}")

@dentist_router.get("/dentists/{dentist_id}", response_model=DentistResponse)
async def get_dentist(dentist_id: int, current_user: dict = Depends(get_current_user)):
    """
    Get a specific dentist by ID
    """
    try:
        dentist = get_dentist_by_id(dentist_id)
        if not dentist:
            raise HTTPException(status_code=404, detail="Dentist not found")
        return dentist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dentist: {str(e)}")

@dentist_router.post("/dentists", response_model=DentistResponse)
async def create_dentist_endpoint(dentist_data: DentistCreate, current_user: dict = Depends(require_admin)):
    """
    Create a new dentist
    """
    try:
        # Check if dentist with same email or license already exists
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM dentists WHERE email = %s OR license = %s", 
                       (dentist_data.email, dentist_data.license))
            existing = cur.fetchone()
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail="Dentist with this email or license already exists"
                )
        
        dentist = create_dentist(dentist_data)
        return dentist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dentist: {str(e)}")

@dentist_router.put("/dentists/{dentist_id}", response_model=DentistResponse)
async def update_dentist_endpoint(dentist_id: int, dentist_data: DentistUpdate, current_user: dict = Depends(require_admin)):
    """
    Update an existing dentist
    """
    try:
        # Check if dentist exists
        existing_dentist = get_dentist_by_id(dentist_id)
        if not existing_dentist:
            raise HTTPException(status_code=404, detail="Dentist not found")
        
        # Check for email/license conflicts if they're being updated
        if dentist_data.email or dentist_data.license:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                email = dentist_data.email or existing_dentist['email']
                license_num = dentist_data.license or existing_dentist['license']
                cur.execute("""
                    SELECT id FROM dentists 
                    WHERE (email = %s OR license = %s) AND id != %s
                """, (email, license_num, dentist_id))
                conflict = cur.fetchone()
                if conflict:
                    raise HTTPException(
                        status_code=400,
                        detail="Another dentist with this email or license already exists"
                    )
        
        dentist = update_dentist(dentist_id, dentist_data)
        return dentist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update dentist: {str(e)}")

@dentist_router.delete("/dentists/{dentist_id}")
async def delete_dentist_endpoint(dentist_id: int, current_user: dict = Depends(require_admin)):
    """
    Delete a dentist
    """
    try:
        # Check if dentist exists
        existing_dentist = get_dentist_by_id(dentist_id)
        if not existing_dentist:
            raise HTTPException(status_code=404, detail="Dentist not found")
        
        # Check if dentist has any appointments
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM appointments WHERE dentist_id = %s", (dentist_id,))
            appointment_count = cur.fetchone()[0]
            if appointment_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete dentist with existing appointments"
                )
        
        success = delete_dentist(dentist_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete dentist")
        
        return {"message": "Dentist deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dentist: {str(e)}")

@dentist_router.get("/dentists/{dentist_id}/appointments")
async def get_dentist_appointments(dentist_id: int, current_user: dict = Depends(require_admin_or_dentist)):
    """
    Get all appointments for a specific dentist
    """
    try:
        # Check if dentist exists
        existing_dentist = get_dentist_by_id(dentist_id)
        if not existing_dentist:
            raise HTTPException(status_code=404, detail="Dentist not found")
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT a.*, d.name as dentist_name
                FROM appointments a
                JOIN dentists d ON a.dentist_id = d.id
                WHERE a.dentist_id = %s
                ORDER BY a.appointment_date, a.appointment_time
            """, (dentist_id,))
            appointments = cur.fetchall()
        
        return appointments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dentist appointments: {str(e)}")

@dentist_router.get("/dentists/specialties")
async def get_dentist_specialties(current_user: dict = Depends(get_current_user)):
    """
    Get all unique dentist specialties
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT specialty FROM dentists ORDER BY specialty")
            specialties = cur.fetchall()
        return [spec['specialty'] for spec in specialties]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch specialties: {str(e)}")
