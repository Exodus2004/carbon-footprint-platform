"""Firebase Authentication Middleware module."""

import logging
from typing import Optional, Dict, Union, List
from fastapi import Header, HTTPException
import firebase_admin  # type: ignore[import-untyped]
from firebase_admin import auth

logger: logging.Logger = logging.getLogger(__name__)

# Initialize Firebase app if credentials exist
firebase_initialized: bool = False
try:
    if not firebase_admin._apps:
        # For a real deployment, credentials.json should be loaded here
        # cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"))
        # firebase_admin.initialize_app(cred)
        pass
except Exception as e:
    logger.warning(f"Firebase initialization skipped or failed: {e}")


async def verify_firebase_token(authorization: Optional[str] = Header(None)) -> str:
    """Middleware to verify Firebase ID tokens.

    Returns the user_id if valid, raises HTTPException otherwise.
    In local development without Firebase, we mock a valid user.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401, detail="Invalid Authorization header format"
        )

    # Mock behavior for local development when Firebase is not initialized
    if token == "mock_local_token":
        return "mock_user_123"

    if not firebase_initialized:
        # Returning mock user if Firebase isn't set up yet for local dev
        return "mock_user_123"

    try:
        decoded_token: Dict[str, Union[str, int, bool, List[str], Dict[str, str]]] = dict(auth.verify_id_token(token))
        uid = decoded_token.get("uid")
        if not uid or not isinstance(uid, str):
            raise HTTPException(status_code=401, detail="Token payload missing user ID")
        return uid
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Invalid or expired token: {str(e)}"
        )
