

# Blu-Reserve 🍽️

**A Touchless Corporate Cafeteria Booking System**

Blu-Reserve is a capacity management tool designed for the post-COVID workplace. It allows employees to reserve specific seats in the cafeteria, ensuring social distancing and equitable access to office resources.

## 🚀 Key Features

* **Interactive Seat Map:** Visual layout with 100 seats divided into 4 Dining Zones (Coffee, Pizza, Asian, Salad).
* **Smart Assign AI:** One-click algorithm to automatically find the best available seat.
* **Friend Finder:** Search for colleagues by **Name** or **IBM Email** to book a seat near them.
* **Simulated SSO:** Mimics the IBM w3id login flow (accepts any valid `@ibm.com` email).
* **Auto-Release Logic:** Seats are automatically vacated if occupied for more than **45 minutes** (to manage rush hour).
* **Blu Dollar Billing:** Bookings are "charged" to the manager's cost center.

## 🛠️ Tech Stack

* **Frontend:** React.js, Vite, Tailwind CSS
* **Backend:** Python FastAPI
* **Testing:** Pytest

---

## ⚡️ Quick Start Guide

### 1. Backend Setup (The API)

*Open a terminal in the `/backend` folder.*

```bash
# 1. Create Virtual Environment
python -m venv venv

# 2. Activate Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Run Server
uvicorn main:app --reload

```

*The backend will start at: `http://127.0.0.1:8000*`

### 2. Frontend Setup (The UI)

*Open a NEW terminal in the `/frontend` folder.*

```bash
# 1. Install Libraries
npm install

# 2. Start Application
npm run dev

```

*The app will open at: `http://localhost:5173*`

---

## 🧪 How to Test (Demo Flow)

1. **Login:**
* Go to `http://localhost:5173`.
* Enter **ANY** email ending in `@ibm.com` (e.g., `tanvi@ibm.com` or `manager@ibm.com`).
* *Note: The system will auto-generate a User Profile based on the email name.*


2. **Book a Seat:**
* Click on any white seat (Available).
* Click **"Confirm Reservation"**.
* The seat turns **Red** (Occupied).


3. **Test Friend Search:**
* In the search bar (top right), type the name of the user you just used (e.g., "Tanvi").
* The seat you booked will highlight in **Yellow**.


4. **Test Auto-Release (45 Min Rule):**
* Click on your occupied seat.
* Look at the receipt panel on the right.
* You will see a countdown: **"Auto-Checkout In: 44m 59s"**.


5. **Smart Assign:**
* Click the **"Smart Assign"** button on the map.
* The system will randomly select an open seat for you.



---

## 📂 Project Structure

```text
BLU-RESERVE-APP/
├── backend/
│   ├── main.py          # All API logic (Auth, Booking, Timer)
│   ├── test_main.py     # Unit tests for requirements
│   └── requirements.txt # Python libraries
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main React UI code
│   │   └── index.css    # Tailwind imports
│   └── package.json     # Node libraries
└── .gitignore           # files to ignore

```
