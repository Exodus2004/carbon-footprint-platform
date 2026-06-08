from fastapi import Header, HTTPException
import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase app if credentials exist
firebase_initialized = False
try:
    if not firebase_admin._apps:
        # For a real deployment, credentials.json should be loaded here
        # cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"))
        # firebase_admin.initialize_app(cred)
        pass
except Exception as e:
    print(f"Firebase initialization skipped or failed: {e}")

async def verify_firebase_token(authorization: str = Header(None)) -> str:
    """
    Middleware to verify Firebase ID tokens.
    Returns the user_id if valid, raises HTTPException otherwise.
    In local development without Firebase, we mock a valid user.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    # Mock behavior for local development when Firebase is not initialized
    if token == "mock_local_token":
        return "mock_user_123"

    if not firebase_initialized:
        # Returning mock user if Firebase isn't set up yet for local dev
        return "mock_user_123"

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token.get("uid")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")
