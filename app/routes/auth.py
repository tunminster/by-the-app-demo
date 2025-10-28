from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
import os
from app.utils.db import conn
from psycopg2.extras import RealDictCursor
import datetime as dt

# Initialize router
auth_router = APIRouter()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str  # Max 72 bytes for bcrypt
    name: str
    role: str = "user"  # Default role for registration
    
    @classmethod
    def validate_password(cls, v):
        """Validate password length for bcrypt (max 72 bytes)"""
        if len(v.encode('utf-8')) > 72:
            raise ValueError("Password cannot be longer than 72 bytes")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# Helper functions
def get_password_hash(password: str) -> str:
    """Hash a password (bcrypt max 72 bytes)"""
    try:
        # Truncate password to 72 bytes if longer (encode to bytes, truncate, decode)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    except Exception as e:
        # If hashing fails for any reason, print error and re-raise
        print(f"Error hashing password: {e}")
        raise ValueError(f"Failed to hash password: {str(e)}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes if longer (for bcrypt compatibility)
    # Note: This means passwords longer than 72 bytes will be truncated
    original_password = plain_password
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        error_msg = str(e).lower()
        # Check for specific bcrypt error about password length
        if "password cannot be longer than 72 bytes" in error_msg:
            # This happens when the hash was created with a password > 72 bytes
            print(f"⚠️  Password verification failed: Hash was created with password > 72 bytes")
            print(f"⚠️  Attempted password length: {len(original_password)} characters, {len(password_bytes)} bytes")
            return False
        # For other errors, just return False
        print(f"⚠️  Password verification failed: {e}")
        return False

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(microsecond=0) + dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(microsecond=0) + dt.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

def update_last_login(user_id: int):
    """Update last login timestamp"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users 
            SET last_login = %s, updated_at = %s
            WHERE id = %s
        """, (datetime.now(timezone.utc), datetime.now(timezone.utc), user_id))

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    # Remove password hash from response
    user_dict = {k: v for k, v in user.items() if k != 'password_hash'}
    return user_dict

# Routes
@auth_router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return access token
    Endpoint: POST /auth/login
    """
    try:
        # Validate password length (bcrypt max 72 bytes)
        password_bytes = len(user_credentials.password.encode('utf-8'))
        if password_bytes > 72:
            raise HTTPException(
                status_code=400,
                detail="Password cannot be longer than 72 bytes. Please contact support if you need to reset your password."
            )
        
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
                detail="Account is deactivated. Please contact administrator."
            )
        
        # Update last login
        update_last_login(user['id'])
        
        # Create access token and refresh token
        access_token = create_access_token(data={"sub": user['username']})
        refresh_token = create_refresh_token(data={"sub": user['username']})
        
        # Remove password hash from response
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=f"Login failed: {error_msg}")

@auth_router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Register a new user (requires admin approval)
    Endpoint: POST /auth/register
    """
    try:
        # Validate password length
        password_bytes = len(user_data.password.encode('utf-8'))
        if password_bytes > 72:
            raise HTTPException(
                status_code=400, 
                detail="Password cannot be longer than 72 bytes. Please use a shorter password."
            )
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
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

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    Endpoint: GET /auth/me
    """
    return current_user

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    Endpoint: POST /auth/refresh
    """
    try:
        # Decode and validate refresh token
        try:
            payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if username is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        except PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        user = get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Create new access token and refresh token
        access_token = create_access_token(data={"sub": user['username']})
        new_refresh_token = create_refresh_token(data={"sub": user['username']})
        
        # Remove password hash from response
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Token refresh failed: {str(e)}"
        )
