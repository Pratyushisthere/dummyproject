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
    expose_headers=["*"]
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
# Add this in your startup event
@app.on_event("startup")
async def startup_db_client():
    # Create indexes
    await seats_collection.create_index("_id")
    await employees_collection.create_index("w3_id", unique=True)
    await employees_collection.create_index("booked_seats")

# ---------------- ROUTES ----------------
@app.get("/seats", response_model=List[Seat])
async def get_seats(user=Depends(get_current_user)):
    return await seats_collection.find().to_list(1000)

@app.post("/book")
async def book(booking: BookingRequest, user=Depends(get_current_user)):
    if not user or "w3_id" not in user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    w3_id = user["w3_id"]
    seat = await seats_collection.find_one({"_id": booking.seat_id})
    
    if not seat or seat.get("status") == "occupied":
        raise HTTPException(status_code=400, detail="Seat unavailable")

    # Start a session for transaction
    async with await client.start_session() as session:
        async with session.start_transaction():
            # Update seat status
            await seats_collection.update_one(
                {"_id": booking.seat_id},
                {"$set": {"status": "occupied", "booked_by": w3_id}},
                session=session
            )

            # Update employee's booked seats
            await employees_collection.update_one(
                {"w3_id": w3_id},
                {
                    "$setOnInsert": {
                        "w3_id": w3_id,
                        "name": user.get("name", "User"),
                        "email": user.get("email", "")
                    },
                    "$addToSet": {"booked_seats": booking.seat_id}
                },
                upsert=True,
                session=session
            )

    return {"message": "Seat booked"}

@app.post("/release/{seat_id}")
async def release(seat_id: int, user=Depends(get_current_user)):
    if not user or "w3_id" not in user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    w3_id = user["w3_id"]
    
    # Start a session for transaction
    async with await client.start_session() as session:
        async with session.start_transaction():
            # Verify the seat is booked by the current user
            seat = await seats_collection.find_one(
                {"_id": seat_id, "booked_by": w3_id},
                session=session
            )
            
            if not seat:
                raise HTTPException(status_code=404, detail="Seat not found or not booked by you")
            
            # Release the seat
            await seats_collection.update_one(
                {"_id": seat_id},
                {"$set": {"status": "available", "booked_by": None}},
                session=session
            )
            
            # Remove from user's booked seats
            await employees_collection.update_one(
                {"w3_id": w3_id},
                {"$pull": {"booked_seats": seat_id}},
                session=session
            )
    
    return {"message": "Seat released"}