from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from auth import router as auth_router, get_current_user

# ---------------- ENV ----------------
MONGO_URL = os.getenv("MONGO_URL")

# ---------------- DB ----------------
client = AsyncIOMotorClient(MONGO_URL)
db = client.office_booking_db
seats_collection = db.seats
employees_collection = db.employees

# ---------------- APP ----------------
app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------
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

# ---------------- STARTUP ----------------
@app.on_event("startup")
async def seed():
    if await seats_collection.count_documents({}) == 0:
        await seats_collection.insert_many(
            [{"_id": i, "status": "available", "price": 5} for i in range(1, 101)]
        )

# ---------------- ROUTES ----------------
@app.get("/seats", response_model=List[Seat])
async def get_seats(user=Depends(get_current_user)):
    return await seats_collection.find().to_list(1000)

@app.post("/book")
async def book(booking: BookingRequest, user=Depends(get_current_user)):
    w3_id = user["w3_id"]
    seat = await seats_collection.find_one({"_id": booking.seat_id})
    if not seat or seat["status"] == "occupied":
        raise HTTPException(status_code=400, detail="Seat unavailable")

    await seats_collection.update_one(
        {"_id": booking.seat_id},
        {"$set": {"status": "occupied", "booked_by": w3_id}},
    )

    await employees_collection.update_one(
        {"w3_id": w3_id},
        {"$addToSet": {"booked_seats": booking.seat_id}},
        upsert=True,
    )

    return {"message": "Seat booked"}

@app.post("/release/{seat_id}")
async def release(seat_id: int, user=Depends(get_current_user)):
    await seats_collection.update_one(
        {"_id": seat_id},
        {"$set": {"status": "available", "booked_by": None}},
    )
    return {"message": "Seat released"}
