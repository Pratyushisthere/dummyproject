import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Annotated
from motor.motor_asyncio import AsyncIOMotorClient

# --- MongoDB Setup ---
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.office_booking_db  # Database name
seats_collection = db.seats
employees_collection = db.employees

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
# Helper to handle MongoDB's _id field
PyObjectId = Annotated[str, BeforeValidator(str)]

class BookingRequest(BaseModel):
    seat_id: int
    w3_id: str
    name: str
    date: str
    time_slot: str

class Seat(BaseModel):
    id: int = Field(alias="_id") # Map MongoDB '_id' to 'id'
    status: str
    price: int
    booked_by: Optional[str] = None
    
    # Simple configuration to allow population by field name
    class Config:
        populate_by_name = True

# --- Lifecycle Events ---
@app.on_event("startup")
async def seed_database():
    """
    On server start, check if seats exist. 
    If not, create 100 seats automatically.
    """
    count = await seats_collection.count_documents({})
    if count == 0:
        print(" seeding database with 100 seats...")
        seat_data = [
            {"_id": i, "status": "available", "price": 5, "booked_by": None}
            for i in range(1, 101)
        ]
        await seats_collection.insert_many(seat_data)
        print("Database seeded!")

# --- Endpoints ---

@app.get("/seats", response_model=List[Seat])
async def get_seats():
    # Fetch all seats from MongoDB
    seats = await seats_collection.find().sort("_id", 1).to_list(1000)
    return seats

@app.post("/book")
async def book_seat(booking: BookingRequest):
    # 1. Find the seat
    seat = await seats_collection.find_one({"_id": booking.seat_id})
    
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
        
    if seat["status"] == "occupied":
        raise HTTPException(status_code=400, detail="Seat taken")

    # 2. Update the Seat Collection
    # We store the full booking details embedded in the seat for now
    await seats_collection.update_one(
        {"_id": booking.seat_id},
        {
            "$set": {
                "status": "occupied",
                "booked_by": booking.w3_id,
                "booking_details": {
                    "name": booking.name,
                    "date": booking.date,
                    "time": booking.time_slot
                }
            }
        }
    )

    # 3. Store/Update Employee Data (Upsert)
    # If employee exists, add seat_id to their history. If not, create them.
    await employees_collection.update_one(
        {"w3_id": booking.w3_id},
        {
            "$set": {"name": booking.name},
            "$addToSet": {"booked_seats": booking.seat_id}
        },
        upsert=True
    )

    # 4. Fetch updated seat to return
    updated_seat = await seats_collection.find_one({"_id": booking.seat_id})
    
    return {
        "message": f"Seat {booking.seat_id} booked. 5 Blu Dollars charged to Manager's Cost Center.", 
        "seat": updated_seat
    }

@app.post("/release/{seat_id}")
async def release_seat(seat_id: int):
    seat = await seats_collection.find_one({"_id": seat_id})
    
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")

    # Update state back to available
    await seats_collection.update_one(
        {"_id": seat_id},
        {
            "$set": {
                "status": "available",
                "booked_by": None,
                "booking_details": None
            }
        }
    )
    
    # Fetch clean version
    updated_seat = await seats_collection.find_one({"_id": seat_id})
    
    return {"message": f"Seat {seat_id} released. Refund processed.", "seat": updated_seat}