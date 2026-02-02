# schemas.py
from datetime import datetime

def employee_document(claims: dict):
    return {
        "w3_id": claims.get("uid") or claims.get("preferred_username"),
        "email": claims.get("email"),
        "full_name": claims.get("name"),
        "manager": claims.get("manager"),
        "department": claims.get("department"),

        # NEW (booking-focused)
        "last_booking_at": None,
        "last_booked_seat": None,
        "blue_tokens_spent": 0, 

        "booked_seats": [],
    }