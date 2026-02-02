from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from datetime import datetime, timedelta

BOOKING_COOLDOWN = timedelta(minutes=45)
SEAT_COST = 5

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

@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {
        "w3_id": user["w3_id"],
        "name": user.get("name"),
        "email": user.get("email"),
    }


@app.get("/seats", response_model=List[Seat])
async def get_seats(user=Depends(get_current_user)):
    return await seats_collection.find().to_list(1000)

@app.post("/book")
async def book_seat(payload: BookingRequest, user=Depends(get_current_user)):
    employee = await employees_collection.find_one({"w3_id": user["w3_id"]})

    # already has an active seat
    if employee and employee.get("last_booked_seat"):
        raise HTTPException(
            status_code=400,
            detail="You already have an active booking. Release it first.",
        )

    # cooldown check ONLY if user still has a seat
    if (
        employee
        and employee.get("last_booked_seat")
        and employee.get("last_booking_at")
    ):
        last = employee["last_booking_at"]
        if datetime.utcnow() - last < BOOKING_COOLDOWN:
            raise HTTPException(
                status_code=400,
                detail="You can book only once every 45 minutes.",
            )


    seat = await seats_collection.find_one({"_id": payload.seat_id})
    if not seat or seat["status"] == "occupied":
        raise HTTPException(status_code=400, detail="Seat unavailable")

    # update seat
    await seats_collection.update_one(
        {"_id": payload.seat_id},
        {
            "$set": {
                "status": "occupied",
                "booked_by": user["w3_id"],
                "booking_time": datetime.utcnow(),
            }
        },
    )

    # update employee (INCLUDING blue tokens)
    await employees_collection.update_one(
        {"w3_id": user["w3_id"]},
        {
            "$addToSet": {"booked_seats": payload.seat_id},
            "$inc": {"blue_tokens_spent": SEAT_COST},
            "$set": {
                "last_booking_at": datetime.utcnow(),
                "last_booked_seat": payload.seat_id,
            },
        },
        upsert=True,
    )

    return {"message": "Seat booked"}

@app.post("/release/{seat_id}")
async def release_seat(seat_id: int, user=Depends(get_current_user)):
    seat = await seats_collection.find_one({"_id": seat_id})

    # seat not owned by user
    if not seat or seat.get("booked_by") != user["w3_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    # release the seat
    await seats_collection.update_one(
        {"_id": seat_id},
        {
            "$set": {
                "status": "available",
                "booked_by": None,
                "booking_time": None,
            }
        },
    )

    # update employee (refund blue tokens + clear booking)
    await employees_collection.update_one(
    {"w3_id": user["w3_id"]},
    {
        "$inc": {"blue_tokens_spent": -SEAT_COST},
        "$pull": {"booked_seats": seat_id},
        "$set": {
            "last_booked_seat": None,
            "last_booking_at": None,  # 👈 reset cooldown
        },
    },
)


    return {
        "message": "Seat released",
        "tokens_refunded": SEAT_COST,
    }


