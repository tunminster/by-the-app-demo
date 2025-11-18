from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime, timezone
import jwt
from jwt import PyJWTError
import os
from app.utils.db import conn
from psycopg2.extras import RealDictCursor, Json
import psycopg2

# Initialize router
settings_router = APIRouter()

# Security setup
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

# Pydantic models
class DayWorkingHours(BaseModel):
    """Working hours for a single day"""
    start: str  # Format: "HH:MM"
    end: str    # Format: "HH:MM"
    closed: bool

class NotificationsSettings(BaseModel):
    """Notification preferences"""
    emailReminders: bool
    smsReminders: bool
    appointmentConfirmations: bool
    newPatientAlerts: bool

class SettingsBase(BaseModel):
    practice_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    working_hours: Dict[str, DayWorkingHours]
    notifications: NotificationsSettings

class SettingsUpdate(BaseModel):
    practice_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    working_hours: Optional[Dict[str, DayWorkingHours]] = None
    notifications: Optional[NotificationsSettings] = None

class SettingsResponse(SettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
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

def require_authenticated_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Require any authenticated user"""
    return current_user

# Database helper functions
def get_settings() -> Optional[dict]:
    """Get settings (singleton - only one record with id=1)"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM settings WHERE id = 1")
        result = cur.fetchone()
        
        # working_hours and notifications are already dicts from psycopg2 JSONB
        # No need to parse them
        
        return result

def create_settings(settings_data: SettingsBase) -> dict:
    """Create settings (singleton - only one record)"""
    # Check if settings already exist
    existing = get_settings()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Settings already exist. Use PUT /api/settings to update."
        )
    
    # Convert working_hours to dict format
    working_hours_dict = {}
    if settings_data.working_hours:
        for day, hours in settings_data.working_hours.items():
            if hasattr(hours, "dict"):
                working_hours_dict[day] = hours.dict()
            else:
                working_hours_dict[day] = hours
    
    # Convert notifications to dict format
    notifications_dict = {}
    if settings_data.notifications:
        if hasattr(settings_data.notifications, "dict"):
            notifications_dict = settings_data.notifications.dict()
        else:
            notifications_dict = settings_data.notifications
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO settings (id, practice_name, address, phone, email, working_hours, notifications)
            VALUES (1, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            RETURNING id, practice_name, address, phone, email, working_hours, notifications, created_at, updated_at
        """, (
            settings_data.practice_name,
            settings_data.address,
            settings_data.phone,
            settings_data.email,
            Json(working_hours_dict),
            Json(notifications_dict)
        ))
        return cur.fetchone()

def update_settings(settings_data: SettingsUpdate) -> Optional[dict]:
    """Update settings"""
    # Check if settings exist
    existing = get_settings()
    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Settings not found. Use POST /api/settings to create."
        )
    
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in settings_data.dict(exclude_unset=True).items():
        if value is not None:
            if field == "working_hours":
                # Convert working_hours to dict format
                working_hours_dict = {}
                if value:
                    for day, hours in value.items():
                        if hasattr(hours, "dict"):
                            working_hours_dict[day] = hours.dict()
                        else:
                            working_hours_dict[day] = hours
                update_fields.append("working_hours = %s::jsonb")
                values.append(Json(working_hours_dict))
            elif field == "notifications":
                # Convert notifications to dict format
                if hasattr(value, "dict"):
                    notifications_dict = value.dict()
                else:
                    notifications_dict = value
                update_fields.append("notifications = %s::jsonb")
                values.append(Json(notifications_dict))
            else:
                update_fields.append(f"{field} = %s")
                values.append(value)
    
    if not update_fields:
        return get_settings()
    
    # Add updated_at timestamp
    update_fields.append("updated_at = %s")
    values.append(datetime.now(timezone.utc))
    
    # Always update id = 1
    values.append(1)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            UPDATE settings 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, practice_name, address, phone, email, working_hours, notifications, created_at, updated_at
        """, values)
        return cur.fetchone()

# API Endpoints

@settings_router.get("/settings", response_model=SettingsResponse)
async def get_settings_endpoint(current_user: dict = Depends(require_authenticated_user)):
    """
    Get current settings (any authenticated user can view)
    """
    try:
        settings = get_settings()
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")

@settings_router.post("/settings", response_model=SettingsResponse)
async def create_settings_endpoint(
    settings_data: SettingsBase,
    current_user: dict = Depends(require_admin)
):
    """
    Create settings (admin only)
    Note: Only one settings record can exist (singleton pattern)
    """
    try:
        settings = create_settings(settings_data)
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create settings: {str(e)}")

@settings_router.put("/settings", response_model=SettingsResponse)
async def update_settings_endpoint(
    settings_data: SettingsUpdate,
    current_user: dict = Depends(require_admin)
):
    """
    Update settings (admin only)
    """
    try:
        settings = update_settings(settings_data)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

