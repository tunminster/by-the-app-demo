from fastapi import APIRouter, HTTPException
from azure.data.tables import TableServiceClient
import bcrypt
import os
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta
from app.utils.azure_utils import get_jwt_secret_key


# FastAPI Router for registration
register_router = APIRouter()

AZURE_CONNECTION_STRING = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
TABLE_NAME = "Users"

# Initialize Table Service Client
table_service = TableServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
table_client = table_service.get_table_client(TABLE_NAME)

# Ensure table exists
# try:
#     table_client.create_table()
# except:
#     pass  # Ignore

# User Signup Model
class UserSignUp(BaseModel):
    email: EmailStr
    password: str

SECRET_KEY = get_jwt_secret_key()
TOKEN_EXPIRY_MINUTES = 60

@register_router.post("/signup") 
async def signup(user: UserSignUp):
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Check if user already exists
    existing_users = table_client.query_entities(f"PartitionKey eq 'user' and RowKey eq '{user.email}'")
    if list(existing_users):
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user entity
    user_entity = {
        "PartitionKey": "user",
        "RowKey": user.email,
        "PasswordHash": hashed_password
    }

    # Insert user into Azure Table Storage
    table_client.create_entity(entity=user_entity)

    return {"message": "User registered successfully"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRY_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

@register_router.post("/signin")
async def signin(user: UserSignUp):
    # Query user from Azure Table Storage
    existing_users = table_client.query_entities(f"PartitionKey eq 'user' and RowKey eq '{user.email}'")
    user_data = list(existing_users)

    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    stored_hashed_password = user_data[0]["PasswordHash"]

    # Verify password
    if not bcrypt.checkpw(user.password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate JWT Token
    access_token = create_access_token({"sub": user.email})

    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}

