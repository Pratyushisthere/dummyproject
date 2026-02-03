# auth.py
import os
import requests
from jose import jwt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import employee_document

router = APIRouter(prefix="/auth")

# ENV
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
TOKEN_URL = os.getenv("TOKEN_URL", "")
AUTH_ENDPOINT = os.getenv("AUTH_ENDPOINT", "")
JWKS_URL = os.getenv("JWKS_URL", "")
JWT_ISSUER = os.getenv("JWT_ISSUER", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# DB
client = AsyncIOMotorClient(MONGO_URL)
db = client.office_booking_db
employees_collection = db.employees

# ---------------- LOGIN ----------------
@router.get("/login")
def login():
    auth_url = (
        f"{AUTH_ENDPOINT}"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid email profile"
    )
    return RedirectResponse(auth_url)

# ---------------- CALLBACK ----------------
@router.get("/ibm/callback")
async def callback(request: Request, code: Optional[str] = None, error: Optional[str] = None):
    # Handle OAuth errors
    if error:
        return RedirectResponse(f"{FRONTEND_URL}?error={error}")
    
    if not code:
        return RedirectResponse(f"{FRONTEND_URL}?error=no_code")
    
    try:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        r = requests.post(TOKEN_URL, data=data, timeout=10)
        token_data = r.json()

        if "id_token" not in token_data:
            return RedirectResponse(f"{FRONTEND_URL}?error=token_exchange_failed")

        claims = jwt.get_unverified_claims(token_data["id_token"])
        w3_id = claims.get("uid") or claims.get("preferred_username")

        if not w3_id:
            return RedirectResponse(f"{FRONTEND_URL}?error=invalid_claims")

        # ---- UPSERT EMPLOYEE ----
        from datetime import datetime
        employee = await employees_collection.find_one({"w3_id": w3_id})
        if not employee:
            await employees_collection.insert_one(employee_document(claims))
        else:
            await employees_collection.update_one(
                {"w3_id": w3_id},
                {"$set": {"last_login_at": datetime.utcnow()}},
            )

        # ---- SESSION ----
        request.session["user"] = {
            "w3_id": w3_id,
            "email": claims.get("email"),
            "name": claims.get("name"),
        }

        return RedirectResponse(FRONTEND_URL)
    
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return RedirectResponse(f"{FRONTEND_URL}?error=auth_failed")

# ---------------- DEPENDENCY ----------------
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
