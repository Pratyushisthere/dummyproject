from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_seats():
    """Check if we have 100 seats"""
    response = client.get("/seats")
    assert response.status_code == 200
    assert len(response.json()) == 100

def test_book_seat():
    """Test booking a specific seat"""
    # 1. Reset first
    client.post("/reset")
    
    # 2. Book Seat 1
    payload = {"seat_id": 1, "w3_id": "test.user@ibm.com", "name": "Test User"}
    response = client.post("/book", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Confirmed for test.user@ibm.com"

    # 3. Try booking it again (Should fail)
    response = client.post("/book", json=payload)
    assert response.status_code == 400  # Should be 'Seat taken'