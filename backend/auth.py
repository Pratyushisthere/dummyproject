# auth.py
import os
import requests
from jose import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import employee_document

router = APIRouter(prefix="/auth")

# ENV
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = os.getenv("TOKEN_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
MONGO_URL = os.getenv("MONGO_URL")

# DB
client = AsyncIOMotorClient(MONGO_URL)
db = client.office_booking_db
employees_collection = db.employees

# ---------------- LOGIN ----------------
@router.get("/login")
def login():
    auth_url = (
        "https://login.w3.ibm.com/oidc/endpoint/default/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid email profile"
    )
    return RedirectResponse(auth_url)

# ---------------- CALLBACK ----------------
@router.get("/ibm/callback")
async def callback(code: str, request: Request):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    r = requests.post(TOKEN_URL, data=data)
    token_data = r.json()

    if "id_token" not in token_data:
        raise HTTPException(400, "Token exchange failed")

    claims = jwt.get_unverified_claims(token_data["id_token"])
    w3_id = claims.get("uid") or claims.get("preferred_username")

    if not w3_id:
        raise HTTPException(401, "Invalid W3ID claims")

    # ---- UPSERT EMPLOYEE ----
    employee = await employees_collection.find_one({"w3_id": w3_id})
    if not employee:
        await employees_collection.insert_one(employee_document(claims))
    else:
        await employees_collection.update_one(
            {"w3_id": w3_id},
            {"$set": {"last_login_at": employee["last_login_at"]}},
        )

    # ---- SESSION ----
    request.session["user"] = {
        "w3_id": w3_id,
        "email": claims.get("email"),
        "name": claims.get("name"),
    }

    return RedirectResponse(FRONTEND_URL)

# ---------------- DEPENDENCY ----------------
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
