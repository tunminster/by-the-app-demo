from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from app.utils.db import conn
from psycopg2.extras import RealDictCursor
import psycopg2

# Initialize router
user_router = APIRouter()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    role: str = "user"  # Default role
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    role: str = "user"  # Default role for registration

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Database helper functions
def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(microsecond=0) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get a single user by ID"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()

def get_user_by_username(username: str) -> Optional[dict]:
    """Get a user by username"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cur.fetchone()

def get_user_by_email(email: str) -> Optional[dict]:
    """Get a user by email"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()

def get_all_users() -> List[dict]:
    """Get all users"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, username, email, name, role, is_active, last_login, created_at, updated_at FROM users ORDER BY created_at DESC")
        return cur.fetchall()

def create_user(user_data: UserCreate) -> dict:
    """Create a new user (admin only)"""
    hashed_password = get_password_hash(user_data.password)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO users (username, email, password_hash, name, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, username, email, name, role, is_active, created_at, updated_at
        """, (
            user_data.username,
            user_data.email,
            hashed_password,
            user_data.name,
            user_data.role,
            user_data.is_active
        ))
        return cur.fetchone()

def register_user(user_data: UserRegister) -> dict:
    """Register a new user (pending admin approval)"""
    hashed_password = get_password_hash(user_data.password)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO users (username, email, password_hash, name, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, username, email, name, role, is_active, created_at, updated_at
        """, (
            user_data.username,
            user_data.email,
            hashed_password,
            user_data.name,
            user_data.role,
            False  # Inactive until admin approval
        ))
        return cur.fetchone()

def approve_user(user_id: int) -> Optional[dict]:
    """Approve a user registration (admin only)"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            UPDATE users 
            SET is_active = true, updated_at = %s
            WHERE id = %s
            RETURNING id, username, email, name, role, is_active, created_at, updated_at
        """, (datetime.now(timezone.utc), user_id))
        return cur.fetchone()

def get_pending_users() -> List[dict]:
    """Get users pending approval"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, username, email, name, role, is_active, created_at, updated_at
            FROM users 
            WHERE is_active = false
            ORDER BY created_at ASC
        """)
        return cur.fetchall()

def update_user(user_id: int, user_data: UserUpdate) -> Optional[dict]:
    """Update an existing user"""
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            if field == "password":
                update_fields.append("password_hash = %s")
                values.append(get_password_hash(value))
            else:
                update_fields.append(f"{field} = %s")
                values.append(value)
    
    if not update_fields:
        return get_user_by_id(user_id)
    
    # Add updated_at timestamp
    update_fields.append("updated_at = %s")
    values.append(datetime.now(timezone.utc))
    
    values.append(user_id)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, username, email, name, role, is_active, last_login, created_at, updated_at
        """, values)
        return cur.fetchone()

def delete_user(user_id: int) -> bool:
    """Delete a user (soft delete by setting is_active to False)"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users 
            SET is_active = False, updated_at = %s
            WHERE id = %s
        """, (datetime.now(timezone.utc), user_id))
        return cur.rowcount > 0

def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users 
            SET last_login = %s, updated_at = %s
            WHERE id = %s
        """, (datetime.now(timezone.utc), datetime.now(timezone.utc), user_id))

def search_users(query: str = None, role: str = None, is_active: bool = None) -> List[dict]:
    """Search users by various criteria"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        conditions = []
        params = []
        
        if query:
            conditions.append("(username ILIKE %s OR email ILIKE %s OR name ILIKE %s)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if role:
            conditions.append("role = %s")
            params.append(role)
        
        if is_active is not None:
            conditions.append("is_active = %s")
            params.append(is_active)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cur.execute(f"""
            SELECT id, username, email, name, role, is_active, last_login, created_at, updated_at
            FROM users 
            WHERE {where_clause}
            ORDER BY created_at DESC
        """, params)
        return cur.fetchall()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
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
    
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    if not user.get('is_active', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user

# Authorization dependencies
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role"""
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def require_admin_or_self(user_id: int, current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role or user accessing their own data"""
    if current_user.get('role') != 'admin' and current_user.get('id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# API Endpoints

@user_router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Register a new user (requires admin approval)
    """
    try:
        # Check if username or email already exists
        existing_username = get_user_by_username(user_data.username)
        existing_email = get_user_by_email(user_data.email)
        
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user = register_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@user_router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return access token
    """
    try:
        # Try to find user by username or email
        user = get_user_by_username(user_credentials.username)
        if not user:
            user = get_user_by_email(user_credentials.username)
        
        if not user or not verify_password(user_credentials.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not user.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        update_last_login(user['id'])
        
        # Create access token
        access_token = create_access_token(data={"sub": user['username']})
        
        # Remove password hash from response
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@user_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@user_router.get("/users", response_model=List[UserResponse])
async def get_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(require_admin)
):
    """
    Get all users (admin only)
    """
    try:
        users = search_users(search, role, is_active)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@user_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: dict = Depends(require_admin_or_self)):
    """
    Get a specific user by ID
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@user_router.post("/users", response_model=UserResponse)
async def create_user_endpoint(user_data: UserCreate, current_user: dict = Depends(require_admin)):
    """
    Create a new user (admin only)
    """
    try:
        # Check if username or email already exists
        existing_username = get_user_by_username(user_data.username)
        existing_email = get_user_by_email(user_data.email)
        
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user = create_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@user_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user_data: UserUpdate, current_user: dict = Depends(require_admin_or_self)):
    """
    Update an existing user
    """
    try:
        # Check if user exists
        existing_user = get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for username/email conflicts if they're being updated
        if user_data.username or user_data.email:
            username = user_data.username or existing_user['username']
            email = user_data.email or existing_user['email']
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id FROM users 
                    WHERE (username = %s OR email = %s) AND id != %s
                """, (username, email, user_id))
                conflict = cur.fetchone()
                if conflict:
                    raise HTTPException(
                        status_code=400,
                        detail="Username or email already exists"
                    )
        
        user = update_user(user_id, user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@user_router.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, current_user: dict = Depends(require_admin)):
    """
    Deactivate a user (admin only)
    """
    try:
        # Check if user exists
        existing_user = get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent admin from deactivating themselves
        if current_user['id'] == user_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate your own account"
            )
        
        success = delete_user(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to deactivate user")
        
        return {"message": "User deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate user: {str(e)}")

@user_router.post("/users/{user_id}/change-password")
async def change_password(user_id: int, password_data: PasswordChange, current_user: dict = Depends(require_admin_or_self)):
    """
    Change user password
    """
    try:
        # Get user
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not verify_password(password_data.current_password, user['password_hash']):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        hashed_password = get_password_hash(password_data.new_password)
        
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET password_hash = %s, updated_at = %s
                WHERE id = %s
            """, (hashed_password, datetime.now(timezone.utc), user_id))
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

@user_router.get("/users/roles")
async def get_user_roles(current_user: dict = Depends(require_admin)):
    """
    Get all available user roles
    """
    return {
        "roles": ["admin", "user", "dentist", "receptionist"],
        "descriptions": {
            "admin": "Full system access",
            "user": "Basic user access",
            "dentist": "Dentist-specific access",
            "receptionist": "Receptionist access"
        }
    }

@user_router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users_endpoint(current_user: dict = Depends(require_admin)):
    """
    Get users pending admin approval
    """
    try:
        pending_users = get_pending_users()
        return pending_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending users: {str(e)}")

@user_router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user_endpoint(user_id: int, current_user: dict = Depends(require_admin)):
    """
    Approve a user registration (admin only)
    """
    try:
        # Check if user exists and is pending
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.get('is_active', False):
            raise HTTPException(status_code=400, detail="User is already active")
        
        approved_user = approve_user(user_id)
        return approved_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve user: {str(e)}")

@user_router.get("/users/stats")
async def get_user_stats(current_user: dict = Depends(require_admin)):
    """
    Get user statistics (admin only)
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Total users
            cur.execute("SELECT COUNT(*) as total FROM users")
            total_users = cur.fetchone()['total']
            
            # Active users
            cur.execute("SELECT COUNT(*) as active FROM users WHERE is_active = true")
            active_users = cur.fetchone()['active']
            
            # Users by role
            cur.execute("""
                SELECT role, COUNT(*) as count 
                FROM users 
                WHERE is_active = true 
                GROUP BY role
            """)
            users_by_role = cur.fetchall()
            
            # Recent logins (last 7 days)
            cur.execute("""
                SELECT COUNT(*) as recent_logins 
                FROM users 
                WHERE last_login >= NOW() - INTERVAL '7 days'
            """)
            recent_logins = cur.fetchone()['recent_logins']
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "users_by_role": users_by_role,
            "recent_logins": recent_logins
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user statistics: {str(e)}")
