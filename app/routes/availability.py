from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, date, time
import jwt
from jwt import PyJWTError
import os
import logging
from app.utils.db import conn
from psycopg2.extras import RealDictCursor, Json
import psycopg2

# Set up logging
logger = logging.getLogger(__name__)

# Initialize router
availability_router = APIRouter()

# Security setup
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

# Pydantic models
class TimeSlot(BaseModel):
    start: str  # Format: "HH:MM"
    end: str    # Format: "HH:MM"
    available: bool

class AvailabilityBase(BaseModel):
    dentist_id: int
    date: date
    time_slots: List[TimeSlot]

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityUpdate(BaseModel):
    time_slots: Optional[List[TimeSlot]] = None

class AvailabilityResponse(BaseModel):
    id: int
    dentist_id: int
    dentist_name: str
    date: date
    time_slots: List[TimeSlot]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AvailabilitySearch(BaseModel):
    dentist_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    available_only: Optional[bool] = None

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
def _get_availability_by_id(availability_id: int) -> Optional[dict]:
    """Get a single availability by ID (internal helper)"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.id = %s
        """, (availability_id,))
        return cur.fetchone()

def _get_availability_by_dentist_and_date(dentist_id: int, date: date) -> Optional[dict]:
    """Get availability for a specific dentist on a specific date (internal helper)"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT a.*, d.name as dentist_name
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.dentist_id = %s AND a.date = %s
        """
        logger.info(f"Querying availability: dentist_id={dentist_id}, date={date}")
        cur.execute(query, (dentist_id, date))
        result = cur.fetchone()
        logger.info(f"Query result: {result}")
        return result

def _normalize_time_str(value) -> Optional[str]:
    """Normalize time representation to HH:MM string"""
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime("%H:%M")
    return str(value)

def _get_time_slot_details(dentist_id: int, slot_date: date, start_time: str):
    """Retrieve availability record, time slots list, and matching slot for given start time"""
    if isinstance(slot_date, str):
        slot_date = datetime.strptime(slot_date, "%Y-%m-%d").date()
    
    normalized_start = _normalize_time_str(start_time)
    record = _get_availability_by_dentist_and_date(dentist_id, slot_date)
    
    if not record:
        return None, None, None
    
    time_slots = record.get("time_slots", [])
    matching_slot = None
    for slot in time_slots:
        if slot.get("start") == normalized_start:
            matching_slot = slot
            break
    
    return record, time_slots, matching_slot

def set_time_slot_availability(
    dentist_id: int,
    slot_date: date,
    start_time,
    available: bool,
    end_time: Optional[str] = None
) -> bool:
    """Set availability flag for a specific time slot"""
    record, time_slots, matching_slot = _get_time_slot_details(dentist_id, slot_date, start_time)
    
    if not record or not time_slots or not matching_slot:
        return False
    
    if end_time:
        normalized_end = _normalize_time_str(end_time)
        if matching_slot.get("end") != normalized_end:
            return False
    
    if matching_slot.get("available") == available:
        return True
    
    matching_slot["available"] = available
    
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE availability 
            SET time_slots = %s::jsonb, updated_at = %s
            WHERE id = %s
        """, (Json(time_slots), datetime.now(timezone.utc), record["id"]))
        return cur.rowcount > 0

def ensure_time_slot_available(
    dentist_id: int,
    slot_date: date,
    start_time
) -> None:
    """Validate that the requested time slot exists and is currently available"""
    record, _, matching_slot = _get_time_slot_details(dentist_id, slot_date, start_time)
    
    if not record:
        raise HTTPException(
            status_code=400,
            detail="Availability is not configured for this dentist on the selected date"
        )
    
    if not matching_slot:
        raise HTTPException(
            status_code=400,
            detail="Requested time slot is not available in the schedule"
        )
    
    if not matching_slot.get("available", False):
        raise HTTPException(
            status_code=400,
            detail="Requested time slot has already been booked"
        )

def get_all_availability() -> List[dict]:
    """Get all availability records"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            ORDER BY a.date, a.dentist_id
        """)
        return cur.fetchall()

def create_availability(availability_data: AvailabilityCreate) -> dict:
    """Create a new availability record"""
    # Check if availability already exists for this dentist and date
    logger.info(f"Creating availability - dentist_id: {availability_data.dentist_id}, date: {availability_data.date}")
    existing = _get_availability_by_dentist_and_date(availability_data.dentist_id, availability_data.date)
    logger.info(f"Existing availability check result: {existing}")
    if existing:
        raise HTTPException(status_code=400, detail="Availability already exists for this dentist on this date")
    
    # Check if dentist exists
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name FROM dentists WHERE id = %s", (availability_data.dentist_id,))
        dentist = cur.fetchone()
        if not dentist:
            raise HTTPException(status_code=404, detail="Dentist not found")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO availability (dentist_id, date, time_slots)
            VALUES (%s, %s, %s::jsonb)
            RETURNING id, dentist_id, date, time_slots, created_at, updated_at
        """, (
            availability_data.dentist_id,
            availability_data.date,
            Json([slot.dict() for slot in availability_data.time_slots])
        ))
        result = cur.fetchone()
        result['dentist_name'] = dentist['name']
        return result

def update_availability(availability_id: int, availability_data: AvailabilityUpdate) -> Optional[dict]:
    """Update an existing availability record"""
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in availability_data.dict(exclude_unset=True).items():
        if value is not None:
            if field == "time_slots":
                update_fields.append("time_slots = %s::jsonb")
                # value is already a list of dicts from .dict()
                values.append(Json(value))
            else:
                update_fields.append(f"{field} = %s")
                values.append(value)
    
    if not update_fields:
        return _get_availability_by_id(availability_id)
    
    # Add updated_at timestamp
    update_fields.append("updated_at = %s")
    values.append(datetime.now(timezone.utc))
    
    values.append(availability_id)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            UPDATE availability 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, dentist_id, date, time_slots, created_at, updated_at
        """, values)
        result = cur.fetchone()
        
        if result:
            # Get dentist name
            with conn.cursor(cursor_factory=RealDictCursor) as dentist_cur:
                dentist_cur.execute("SELECT name FROM dentists WHERE id = %s", (result['dentist_id'],))
                dentist = dentist_cur.fetchone()
                result['dentist_name'] = dentist['name'] if dentist else None
        
        return result

def delete_availability(availability_id: int) -> bool:
    """Delete an availability record"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM availability WHERE id = %s", (availability_id,))
        return cur.rowcount > 0

def search_availability(
    dentist_id: int = None,
    date_from: date = None,
    date_to: date = None,
    available_only: bool = None
) -> List[dict]:
    """Search availability by various criteria"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        conditions = []
        params = []
        
        if dentist_id:
            conditions.append("a.dentist_id = %s")
            params.append(dentist_id)
        
        if date_from:
            conditions.append("a.date >= %s")
            params.append(date_from)
        
        if date_to:
            conditions.append("a.date <= %s")
            params.append(date_to)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cur.execute(f"""
            SELECT a.*, d.name as dentist_name
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE {where_clause}
            ORDER BY a.date, a.dentist_id
        """, params)
        results = cur.fetchall()
        
        # Filter by available slots if requested
        if available_only:
            filtered_results = []
            for result in results:
                available_slots = [slot for slot in result['time_slots'] if slot.get('available', False)]
                if available_slots:
                    result['time_slots'] = available_slots
                    filtered_results.append(result)
            return filtered_results
        
        return results

def get_available_slots_by_dentist(dentist_id: int, date: date) -> List[dict]:
    """Get available time slots for a specific dentist on a specific date"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, d.name as dentist_name
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.dentist_id = %s AND a.date = %s
        """, (dentist_id, date))
        result = cur.fetchone()
        
        if not result:
            return []
        
        # Filter only available slots
        available_slots = [slot for slot in result['time_slots'] if slot.get('available', False)]
        result['time_slots'] = available_slots
        return [result] if available_slots else []

def book_time_slot(availability_id: int, time_slot: TimeSlot) -> bool:
    """Book a specific time slot"""
    with conn.cursor() as cur:
        # Get current availability
        cur.execute("SELECT time_slots FROM availability WHERE id = %s", (availability_id,))
        result = cur.fetchone()
        
        if not result:
            return False
        
        time_slots = result[0]
        
        # Find and update the specific time slot
        for slot in time_slots:
            if slot['start'] == time_slot.start and slot['end'] == time_slot.end:
                slot['available'] = False
                break
        
        # Update the availability record
        cur.execute("""
            UPDATE availability 
            SET time_slots = %s::jsonb, updated_at = %s
            WHERE id = %s
        """, (Json(time_slots), datetime.now(timezone.utc), availability_id))
        
        return cur.rowcount > 0

def release_time_slot(availability_id: int, time_slot: TimeSlot) -> bool:
    """Release a specific time slot"""
    with conn.cursor() as cur:
        # Get current availability
        cur.execute("SELECT time_slots FROM availability WHERE id = %s", (availability_id,))
        result = cur.fetchone()
        
        if not result:
            return False
        
        time_slots = result[0]
        
        # Find and update the specific time slot
        for slot in time_slots:
            if slot['start'] == time_slot.start and slot['end'] == time_slot.end:
                slot['available'] = True
                break
        
        # Update the availability record
        cur.execute("""
            UPDATE availability 
            SET time_slots = %s::jsonb, updated_at = %s
            WHERE id = %s
        """, (Json(time_slots), datetime.now(timezone.utc), availability_id))
        
        return cur.rowcount > 0

def get_availability_statistics() -> dict:
    """Get availability statistics"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Total availability records
        cur.execute("SELECT COUNT(*) as total FROM availability")
        total_availability = cur.fetchone()['total']
        
        # Availability by dentist
        cur.execute("""
            SELECT d.name as dentist_name, COUNT(a.id) as availability_count
            FROM dentists d
            LEFT JOIN availability a ON d.id = a.dentist_id
            GROUP BY d.id, d.name
            ORDER BY availability_count DESC
        """)
        availability_by_dentist = cur.fetchall()
        
        # Total available slots
        cur.execute("""
            SELECT COUNT(*) as total_slots
            FROM availability, jsonb_array_elements(time_slots) as slot
            WHERE (slot->>'available')::boolean = true
        """)
        total_available_slots = cur.fetchone()['total_slots']
        
        # Total booked slots
        cur.execute("""
            SELECT COUNT(*) as total_booked_slots
            FROM availability, jsonb_array_elements(time_slots) as slot
            WHERE (slot->>'available')::boolean = false
        """)
        total_booked_slots = cur.fetchone()['total_booked_slots']
        
        # Upcoming availability (next 7 days)
        cur.execute("""
            SELECT COUNT(*) as upcoming_availability
            FROM availability
            WHERE date >= CURRENT_DATE AND date <= CURRENT_DATE + INTERVAL '7 days'
        """)
        upcoming_availability = cur.fetchone()['upcoming_availability']
    
    return {
        "total_availability_records": total_availability,
        "total_available_slots": total_available_slots,
        "total_booked_slots": total_booked_slots,
        "availability_by_dentist": availability_by_dentist,
        "upcoming_availability": upcoming_availability
    }

# API Endpoints

@availability_router.get("/availability", response_model=List[AvailabilityResponse])
async def get_availability(
    dentist_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    available_only: Optional[bool] = None,
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get availability records with optional filtering
    """
    try:
        availability = search_availability(dentist_id, date_from, date_to, available_only)
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch availability: {str(e)}")

@availability_router.get("/availability/{availability_id}", response_model=AvailabilityResponse)
async def get_availability_by_id(availability_id: int, current_user: dict = Depends(require_authenticated_user)):
    """
    Get a specific availability record by ID
    """
    try:
        availability = _get_availability_by_id(availability_id)
        if not availability:
            raise HTTPException(status_code=404, detail="Availability record not found")
        return availability
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch availability: {str(e)}")

@availability_router.get("/availability/dentist/{dentist_id}/date/{date}")
async def get_availability_by_dentist_and_date(
    dentist_id: int, 
    date: date, 
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get availability for a specific dentist on a specific date
    """
    try:
        availability = _get_availability_by_dentist_and_date(dentist_id, date)
        if not availability:
            raise HTTPException(status_code=404, detail="No availability found for this dentist on this date")
        return availability
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch availability: {str(e)}")

@availability_router.get("/availability/dentist/{dentist_id}/available")
async def get_available_slots(
    dentist_id: int,
    date: date,
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Get only available time slots for a specific dentist on a specific date
    """
    try:
        available_slots = get_available_slots_by_dentist(dentist_id, date)
        return available_slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch available slots: {str(e)}")

@availability_router.post("/availability", response_model=AvailabilityResponse)
async def create_availability_endpoint(
    availability_data: AvailabilityCreate, 
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Create a new availability record
    """
    try:
        availability = create_availability(availability_data)
        return availability
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create availability: {str(e)}")

@availability_router.put("/availability/{availability_id}", response_model=AvailabilityResponse)
async def update_availability_endpoint(
    availability_id: int, 
    availability_data: AvailabilityUpdate, 
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Update an existing availability record
    """
    try:
        # Check if availability exists
        existing_availability = _get_availability_by_id(availability_id)
        if not existing_availability:
            raise HTTPException(status_code=404, detail="Availability record not found")
        
        availability = update_availability(availability_id, availability_data)
        return availability
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update availability: {str(e)}")

@availability_router.delete("/availability/{availability_id}")
async def delete_availability_endpoint(
    availability_id: int, 
    current_user: dict = Depends(require_admin)
):
    """
    Delete an availability record (admin only)
    """
    try:
        # Check if availability exists
        existing_availability = _get_availability_by_id(availability_id)
        if not existing_availability:
            raise HTTPException(status_code=404, detail="Availability record not found")
        
        success = delete_availability(availability_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete availability record")
        
        return {"message": "Availability record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete availability: {str(e)}")

@availability_router.post("/availability/{availability_id}/book-slot")
async def book_time_slot_endpoint(
    availability_id: int,
    time_slot: TimeSlot,
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Book a specific time slot
    """
    try:
        success = book_time_slot(availability_id, time_slot)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to book time slot")
        
        return {"message": "Time slot booked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to book time slot: {str(e)}")

@availability_router.post("/availability/{availability_id}/release-slot")
async def release_time_slot_endpoint(
    availability_id: int,
    time_slot: TimeSlot,
    current_user: dict = Depends(require_admin_or_receptionist)
):
    """
    Release a specific time slot
    """
    try:
        success = release_time_slot(availability_id, time_slot)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to release time slot")
        
        return {"message": "Time slot released successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to release time slot: {str(e)}")

@availability_router.get("/availability/stats")
async def get_availability_stats(current_user: dict = Depends(require_admin)):
    """
    Get availability statistics (admin only)
    """
    try:
        stats = get_availability_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch availability statistics: {str(e)}")
