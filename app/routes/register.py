from flask import Blueprint
from fastapi import FastAPI, HTTPException
from azure.data.tables import TableServiceClient
import bcrypt
import os
from pydantic import BaseModel, EmailStr

register_bp = Blueprint('register_bp', __name__)

AZURE_CONNECTION_STRING = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
TABLE_NAME = "Users"

# Initialize Table Service Client
table_service = TableServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
table_client = table_service.get_table_client(TABLE_NAME)

# Ensure table exists
try:
    table_client.create_table()
except:
    pass  # Ignore

# User Signup Model
class UserSignUp(BaseModel):
    email: EmailStr
    password: str



@register_bp.post("/signup") 
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

