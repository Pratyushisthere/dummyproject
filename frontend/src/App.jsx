import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [seats, setSeats] = useState([]);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [notification, setNotification] = useState(null);
  const [selectedDate, setSelectedDate] = useState("Today");
  const [selectedTime, setSelectedTime] = useState("12:00 PM");

  // --- Axios instance (cookie-based auth) ---
  const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    withCredentials: true, // 🔐 REQUIRED for W3ID session cookie
  });

  // --- Check session on mount ---
  useEffect(() => {
    api
      .get("/seats")
      .then(() => setIsLoggedIn(true))
      .catch(() => setIsLoggedIn(false));
  }, []);

  // --- Fetch seats periodically ---
  useEffect(() => {
    if (!isLoggedIn) return;

    fetchSeats();
    const interval = setInterval(fetchSeats, 2000);
    return () => clearInterval(interval);
  }, [isLoggedIn]);

  const fetchSeats = async () => {
    try {
      const res = await api.get("/seats");
      const normalizedSeats = res.data.map((seat) => ({
        ...seat,
        id: seat.id || seat._id,
      }));
      setSeats(normalizedSeats);

      if (selectedSeat) {
        const updatedSeat = normalizedSeats.find(
          (s) => s.id === selectedSeat.id
        );
        if (updatedSeat) setSelectedSeat(updatedSeat);
      }
    } catch (err) {
      console.error(err);
      setNotification({
        type: "error",
        message: "Failed to fetch seats. Are you logged in?",
      });
      setTimeout(() => setNotification(null), 3000);
      setIsLoggedIn(false);
    }
  };

  // --- Login via backend (IBM W3ID handled server-side) ---
  const handleLogin = () => {
    window.location.href = "http://127.0.0.1:8000/auth/login";
  };

  // --- Booking ---
  const handleBooking = async () => {
    if (!selectedSeat) return;
    try {
      await api.post("/book", {
        seat_id: selectedSeat.id,
        name: "Employee",
        date: selectedDate,
        time_slot: selectedTime,
      });
      setNotification({
        type: "success",
        message: `Seat ${selectedSeat.id} Reserved`,
      });
      fetchSeats();
    } catch (err) {
      setNotification({ type: "error", message: "Booking Failed." });
    }
    setTimeout(() => setNotification(null), 4000);
  };

  // --- Checkout ---
  const handleCheckout = async () => {
    if (!selectedSeat) return;
    try {
      await api.post(`/release/${selectedSeat.id}`);
      setNotification({
        type: "success",
        message: `Checked out of Seat ${selectedSeat.id}`,
      });
      fetchSeats();
    } catch (err) {
      setNotification({ type: "error", message: "Checkout Failed." });
    }
    setTimeout(() => setNotification(null), 3000);
  };

  // --- Auto-select seat ---
  const autoSelectSeat = () => {
    const availableSeats = seats.filter((s) => s.status === "available");
    if (!availableSeats.length) {
      setNotification({ type: "error", message: "No seats available!" });
      return;
    }
    const randomBest =
      availableSeats[Math.floor(Math.random() * availableSeats.length)];
    setSelectedSeat(randomBest);
    setNotification({
      type: "success",
      message: `AI selected Seat #${randomBest.id}`,
    });
  };

  // --- Search ---
  const isSearched = (seat) => {
    if (!searchQuery) return false;
    const query = searchQuery.toLowerCase();
    if (seat.user_details?.full_name?.toLowerCase().includes(query))
      return true;
    if (seat.booked_by?.toLowerCase().includes(query)) return true;
    return false;
  };

  // --- Time left ---
  const getTimeLeft = (bookingTimeStr) => {
    if (!bookingTimeStr) return "45m 00s";
    const bookedAt = new Date(bookingTimeStr).getTime();
    const expiresAt = bookedAt + 45 * 60 * 1000;
    const diff = expiresAt - Date.now();
    if (diff <= 0) return "Expiring...";
    const minutes = Math.floor(diff / (1000 * 60));
    return `${minutes}m left`;
  };

  const getZoneStyle = (id) => {
    if (id <= 25)
      return "border-blue-200 bg-blue-50 text-blue-400 hover:border-blue-500 hover:bg-blue-100";
    if (id <= 50)
      return "border-orange-200 bg-orange-50 text-orange-400 hover:border-orange-500 hover:bg-orange-100";
    if (id <= 75)
      return "border-red-200 bg-red-50 text-red-400 hover:border-red-500 hover:bg-red-100";
    return "border-green-200 bg-green-50 text-green-400 hover:border-green-500 hover:bg-green-100";
  };

  const FoodStall = ({ name, emoji, color, position, desc }) => (
    <div
      className={`absolute ${position} flex flex-col items-center z-20 group cursor-help`}
    >
      <div
        className={`w-12 h-12 ${color} rounded-full shadow-lg border-4 border-white flex items-center justify-center text-2xl transform transition-transform group-hover:scale-110`}
      >
        {emoji}
      </div>
      <div className="bg-white px-3 py-1 rounded-full shadow-md border border-stone-200 mt-2 -space-y-0.5 text-center">
        <p className="text-[10px] font-bold uppercase tracking-wider text-stone-800">
          {name}
        </p>
        <p className="text-[8px] text-stone-400 font-medium">{desc}</p>
      </div>
    </div>
  );

  // --- LOGIN SCREEN ---
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-stone-200 text-center">
          <h1 className="text-3xl font-serif font-bold text-[#4A403A] mb-2">
            Blu-Reserve
          </h1>
          <p className="text-stone-500 mb-8 text-sm">
            Workplace Capacity Management
          </p>
          <button
            onClick={handleLogin}
            className="w-full bg-[#4A403A] text-white py-4 rounded-xl font-bold shadow-lg hover:bg-[#38302C] transition-all"
          >
            Sign In with IBM W3ID
          </button>
        </div>
      </div>
    );
  }

  // --- MAIN APP SCREEN ---
  return (
    <div className="min-h-screen bg-stone-100 text-stone-800 font-sans p-4 md:p-8">
      {/* YOUR EXISTING UI RENDERS HERE */}
    </div>
  );
};

export default App;
