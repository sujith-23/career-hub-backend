"""
Verifies Firebase ID tokens sent from the frontend, so protected endpoints
know which logged-in user is making the request.

Setup required (see README):
1. In Firebase console -> Project settings -> Service accounts ->
   "Generate new private key". This downloads a JSON file.
2. Save it as `backend/firebase-service-account.json` (NOT committed to git).
3. Set env var GOOGLE_APPLICATION_CREDENTIALS to that file path, or just
   drop it at the default path this module looks for.
"""
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
    """
    Reads `Authorization: Bearer <firebase_id_token>` header, verifies it,
    and returns the Firebase UID. Raises 401 if missing/invalid.
    """
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


async def get_current_user_optional(authorization: str = Header(None)):
    """
    Like get_current_user, but returns None instead of raising when there's
    no token or it's invalid — used for endpoints like /api/track that work
    whether or not the student is logged in, but record who it was if they are.
    Returns a dict {uid, email} or None.
    """
    if _firebase_app is None or not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        decoded = auth.verify_id_token(token)
        return {"uid": decoded["uid"], "email": decoded.get("email")}
    except Exception:
        return None


# Comma-separated list of emails allowed to view per-student analytics.
# Set this env var in production — e.g. ADMIN_EMAILS=you@gmail.com,mentor@gmail.com
_ADMIN_EMAILS = {
    e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()
}


async def require_admin(authorization: str = Header(None)) -> str:
    """
    Verifies the token AND checks the user's email is in the ADMIN_EMAILS
    allowlist. Raises 403 otherwise. Use this for endpoints that expose
    individual (not aggregated) student data.
    """
    uid = await get_current_user(authorization)
    token = authorization.split(" ", 1)[1]
    decoded = auth.verify_id_token(token)
    email = (decoded.get("email") or "").lower()
    if not _ADMIN_EMAILS:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_EMAILS is not configured on the backend — no one is authorized yet.",
        )
    if email not in _ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Not authorized to view student-level data.")
    return uid
