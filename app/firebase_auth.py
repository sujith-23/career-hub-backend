
import os
from dotenv import load_dotenv

load_dotenv()

import firebase_admin

from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "firebase-service-account.json"
    ),
)

_firebase_app = None

if os.path.exists(_SERVICE_ACCOUNT_PATH):
    cred = credentials.Certificate(_SERVICE_ACCOUNT_PATH)
    _firebase_app = firebase_admin.initialize_app(cred)

security = HTTPBearer()


async def get_current_user(
    credentials_data: HTTPAuthorizationCredentials = Depends(security),
) -> str:

    if _firebase_app is None:
        raise HTTPException(
            status_code=500,
            detail="Backend is missing Firebase service account.",
        )

    token = credentials_data.credentials

    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {e}",
        )


async def get_current_user_optional(
    credentials_data: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
):
    if _firebase_app is None or credentials_data is None:
        return None

    token = credentials_data.credentials

    try:
        decoded = auth.verify_id_token(token)

        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
        }

    except Exception:
        return None


_ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.getenv("ADMIN_EMAILS", "").split(",")
    if e.strip()
}


async def require_admin(
    credentials_data: HTTPAuthorizationCredentials = Depends(security),
) -> str:

    uid = await get_current_user(credentials_data)

    token = credentials_data.credentials

    try:
        decoded = auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {e}",
        )

    email = (decoded.get("email") or "").lower()

    if not _ADMIN_EMAILS:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_EMAILS is not configured on the backend.",
        )

    if email not in _ADMIN_EMAILS:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view student-level data.",
        )

    return uid