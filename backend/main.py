from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Updated Data Models ---
class BookingRequest(BaseModel):
    seat_id: int
    w3_id: str
    name: str
    date: str       # New: "Today", "Tomorrow", etc.
    time_slot: str  # New: "12:00 PM", "12:30 PM"

class Seat(BaseModel):
    id: int
    status: str
    price: int      # Price in Blu Dollars
    booked_by: Optional[str] = None

# --- Mock Database ---
seats_db = [
    {"id": i, "status": "available", "price": 5, "booked_by": None}
    for i in range(1, 101) 
]

@app.get("/seats", response_model=List[Seat])
async def get_seats():
    return seats_db

@app.post("/book")
async def book_seat(booking: BookingRequest):
    for seat in seats_db:
        if seat["id"] == booking.seat_id:
            if seat["status"] == "occupied":
                raise HTTPException(status_code=400, detail="Seat taken")
            
            seat["status"] = "occupied"
            seat["booked_by"] = booking.w3_id
            
            # Message confirms the Blu Dollar charge
            return {
                "message": f"Seat {seat['id']} booked. 5 Blu Dollars charged to Manager's Cost Center.", 
                "seat": seat
            }
            
    raise HTTPException(status_code=404, detail="Seat not found")

@app.post("/release/{seat_id}")
async def release_seat(seat_id: int):
    for seat in seats_db:
        if seat["id"] == seat_id:
            seat["status"] = "available"
            seat["booked_by"] = None
            return {"message": f"Seat {seat_id} released. Refund processed.", "seat": seat}
    raise HTTPException(status_code=404, detail="Seat not found")