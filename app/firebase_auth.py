import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Header, HTTPException

_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    os.path.join(os.path.dirname(__file__), "..", "firebase-service-account.json"),
)

_firebase_app = None
if os.path.exists(_SERVICE_ACCOUNT_PATH):
    cred = credentials.Certificate(_SERVICE_ACCOUNT_PATH)
    _firebase_app = firebase_admin.initialize_app(cred)


async def get_current_user(authorization: str = Header(None)) -> str:
    if _firebase_app is None:
        raise HTTPException(
            status_code=500,
            detail="Backend is missing firebase-service-account.json — see README.",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization.split(" ", 1)[1]
    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")