# schemas.py
from datetime import datetime

def employee_document(claims: dict):
    return {
        "w3_id": claims.get("uid") or claims.get("preferred_username"),
        "email": claims.get("email"),
        "full_name": claims.get("name"),
        "manager": claims.get("manager"),
        "department": claims.get("department"),
        "first_login_at": datetime.utcnow(),
        "last_login_at": datetime.utcnow(),
        "booked_seats": [],
    }
