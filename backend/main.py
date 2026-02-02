from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
import os

from auth import router as auth_router, get_current_user

# ENV
MONGO_URL = os.getenv("MONGO_URL")
SESSION_SECRET = os.getenv("SESSION_SECRET")

# DB
client = AsyncIOMotorClient(MONGO_URL)
db = client.office_booking_db
seats_collection = db.seats
employees_collection = db.employees

# APP
app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False,
)

# MODELS
class Seat(BaseModel):
    id: int = Field(alias="_id")
    status: str
    price: int
    booked_by: Optional[str] = None

    class Config:
        populate_by_name = True

class BookingRequest(BaseModel):
    seat_id: int
    date: str
    time_slot: str

# STARTUP
@app.on_event("startup")
async def seed():
    if await seats_collection.count_documents({}) == 0:
        await seats_collection.insert_many(
            [{"_id": i, "status": "available", "price": 5} for i in range(1, 101)]
        )

# ROUTES
@app.get("/seats", response_model=List[Seat])
async def get_seats(user=Depends(get_current_user)):
    return await seats_collection.find().to_list(1000)

@app.post("/book")
async def book_seat(payload: BookingRequest, user=Depends(get_current_user)):
    seat = await seats_collection.find_one({"_id": payload.seat_id})
    if not seat or seat["status"] == "occupied":
        raise HTTPException(400, "Seat unavailable")

    await seats_collection.update_one(
        {"_id": payload.seat_id},
        {"$set": {"status": "occupied", "booked_by": user["w3_id"]}},
    )

    await employees_collection.update_one(
        {"w3_id": user["w3_id"]},
        {"$addToSet": {"booked_seats": payload.seat_id}},
    )

    return {"message": "Seat booked"}

@app.post("/release/{seat_id}")
async def release_seat(seat_id: int, user=Depends(get_current_user)):
    await seats_collection.update_one(
        {"_id": seat_id},
        {"$set": {"status": "available", "booked_by": None}},
    )
    return {"message": "Seat released"}
