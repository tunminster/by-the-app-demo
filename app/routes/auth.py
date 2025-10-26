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

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    role: str = "user"  # Default role for registration

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

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
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(microsecond=0) + dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
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

@auth_router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Register a new user (requires admin approval)
    Endpoint: POST /auth/register
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

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    Endpoint: GET /auth/me
    """
    return current_user
