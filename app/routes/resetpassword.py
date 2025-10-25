from fastapi import APIRouter, HTTPException
from azure.data.tables import TableServiceClient
import bcrypt
import os
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.utils.azure_utils import get_jwt_secret_key

# FastAPI Router for password reset
reset_router = APIRouter()

AZURE_CONNECTION_STRING = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
TABLE_NAME = "Users"
SENDGRID_API_KEY = os.getenv("SendGrid-Api-Key")
SENDER_EMAIL = "no-reply@ragibull.com"  # Replace with your verified SendGrid sender email
SECRET_KEY = get_jwt_secret_key()
TOKEN_EXPIRY_MINUTES = 30  # Expiry time for reset token

# Initialize Table Service Client
table_service = TableServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
table_client = table_service.get_table_client(TABLE_NAME)

# Request Password Reset Model
class PasswordResetRequest(BaseModel):
    email: EmailStr

# Reset Password Model
class ResetPassword(BaseModel):
    token: str
    new_password: str

def create_reset_token(email: str):
    """Generate a JWT token for password reset"""
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm="HS256")

def send_reset_email(to_email: str, reset_link: str):
    """Send password reset email using SendGrid."""
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject="Password Reset Request",
        html_content=f"""
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">{reset_link}</a>
            <p>This link will expire in {TOKEN_EXPIRY_MINUTES} minutes.</p>
        """
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@reset_router.post("/request-password-reset")
async def request_password_reset(data: PasswordResetRequest):
    """Endpoint to request a password reset"""
    existing_users = table_client.query_entities(f"PartitionKey eq 'user' and RowKey eq '{data.email}'")
    user_data = list(existing_users)

    if not user_data:
        raise HTTPException(status_code=400, detail="User not found")

    # Generate reset token and link
    reset_token = create_reset_token(data.email)
    reset_link = f"https://yourfrontend.com/reset-password?token={reset_token}"

    # Send the reset email
    send_reset_email(data.email, reset_link)

    return {"message": "Reset link sent! Check your email."}

@reset_router.post("/reset-password")
async def reset_password(data: ResetPassword):
    """Endpoint to reset password"""
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=["HS256"])
        email = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    # Query user
    existing_users = table_client.query_entities(f"PartitionKey eq 'user' and RowKey eq '{email}'")
    user_data = list(existing_users)

    if not user_data:
        raise HTTPException(status_code=400, detail="User not found")

    # Hash new password
    hashed_password = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Update password in Azure Table Storage
    user_entity = user_data[0]
    user_entity["PasswordHash"] = hashed_password
    table_client.update_entity(mode="Merge", entity=user_entity)

    return {"message": "Password reset successful"}
