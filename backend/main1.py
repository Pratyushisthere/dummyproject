from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt
import requests
import os
from dotenv import load_dotenv

# ----------------- ENV -----------------
load_dotenv()
JWKS_URL = os.getenv("JWKS_URL")          # IBM JWKS URL
ISSUER = os.getenv("JWT_ISSUER")          # IBM JWT issuer
MONGO_URL = os.getenv("MONGO_URL")        # MongoDB connection string

if not JWKS_URL or not ISSUER or not MONGO_URL:
    raise RuntimeError("JWKS_URL, JWT_ISSUER, and MONGO_URL must be set")

# ----------------- SECURITY -----------------
security = HTTPBearer()

def get_jwks():
    try:
        return requests.get(JWKS_URL, timeout=5).json()
    except Exception:
        raise HTTPException(status_code=503, detail="Unable to fetch JWKS")

def verify_jwt(token: str):
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    jwks = get_jwks()
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token key")
    
    return jwt.decode(token, key, algorithms=["RS256"], issuer=ISSUER)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = verify_jwt(creds.credentials)
        return {
            "w3_id": payload["sub"],
            "name": payload.get("name"),
            "email": payload.get("email"),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired W3ID token")

# ----------------- DATABASE -----------------
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database("office_booking_db")
seats_collection = db.seats
employees_collection = db.employees

# ----------------- FASTAPI APP -----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; lock this to your frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- MODELS -----------------
class BookingRequest(BaseModel):
    seat_id: int
    name: str
    date: str
    time_slot: str

class Seat(BaseModel):
    id: int = Field(alias="_id")
    status: str
    price: int
    booked_by: Optional[str] = None

    class Config:
        populate_by_name = True

# ----------------- STARTUP EVENT -----------------
@app.on_event("startup")
async def seed_database():
    count = await seats_collection.count_documents({})
    if count == 0:
        seat_data = [{"_id": i, "status": "available", "price": 5, "booked_by": None} for i in range(1, 101)]
        await seats_collection.insert_many(seat_data)
        print("Database seeded with 100 seats")

# ----------------- ROUTES -----------------
@app.get("/seats", response_model=List[Seat])
async def get_seats(user=Depends(get_current_user)):
    return await seats_collection.find().sort("_id", 1).to_list(1000)

@app.post("/book")
async def book_seat(booking: BookingRequest, user=Depends(get_current_user)):
    w3_id = user["w3_id"]
    seat = await seats_collection.find_one({"_id": booking.seat_id})
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    if seat["status"] == "occupied":
        raise HTTPException(status_code=400, detail="Seat already occupied")

    await seats_collection.update_one(
        {"_id": booking.seat_id},
        {"$set": {
            "status": "occupied",
            "booked_by": w3_id,
            "booking_details": {
                "name": booking.name,
                "date": booking.date,
                "time": booking.time_slot,
            }
        }}
    )

    await employees_collection.update_one(
        {"w3_id": w3_id},
        {"$set": {"name": booking.name}, "$addToSet": {"booked_seats": booking.seat_id}},
        upsert=True
    )

    updated_seat = await seats_collection.find_one({"_id": booking.seat_id})
    return {"message": f"Seat {booking.seat_id} booked. 5 Blu Dollars charged.", "seat": updated_seat}

@app.post("/release/{seat_id}")
async def release_seat(seat_id: int, user=Depends(get_current_user)):
    seat = await seats_collection.find_one({"_id": seat_id})
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")

    await seats_collection.update_one(
        {"_id": seat_id},
        {"$set": {"status": "available", "booked_by": None, "booking_details": None}}
    )
    updated_seat = await seats_collection.find_one({"_id": seat_id})
    return {"message": f"Seat {seat_id} released successfully.", "seat": updated_seat}
