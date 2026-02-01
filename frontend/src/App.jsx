import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [seats, setSeats] = useState([]);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [w3Id, setW3Id] = useState(""); 
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  // --- RESTORED: Search State ---
  const [searchQuery, setSearchQuery] = useState("");
  const [notification, setNotification] = useState(null);

  // Filters
  const [selectedDate, setSelectedDate] = useState("Today");
  const [selectedTime, setSelectedTime] = useState("12:00 PM");

  useEffect(() => { 
    fetchSeats(); 
    const interval = setInterval(fetchSeats, 2000); 
    return () => clearInterval(interval);
  }, []);

  const fetchSeats = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/seats');
      setSeats(res.data);
      if (selectedSeat) {
        const updatedSeat = res.data.find(s => s.id === selectedSeat.id);
        if (updatedSeat) setSelectedSeat(updatedSeat);
      }
    } catch (err) { console.error(err); }
  };

  const handleLogin = () => {
    if (!w3Id.toLowerCase().includes("ibm.com")) {
      alert("Please enter a valid IBM w3 ID");
      return;
    }
    setIsLoggedIn(true);
  };

  const handleBooking = async () => {
    if (!selectedSeat) return;
    try {
      await axios.post(`http://127.0.0.1:8000/book`, {
        seat_id: selectedSeat.id,
        w3_id: w3Id,
        name: "Employee",
        date: selectedDate,
        time_slot: selectedTime
      });
      setNotification({ type: 'success', message: `Seat ${selectedSeat.id} Reserved` });
      fetchSeats();
    } catch (err) {
      setNotification({ type: 'error', message: 'Booking Failed.' });
    }
    setTimeout(() => setNotification(null), 4000);
  };

  const handleCheckout = async () => {
     if (!selectedSeat) return;
     try {
       await axios.post(`http://127.0.0.1:8000/release/${selectedSeat.id}`);
       setNotification({ type: 'success', message: `Checked out of Seat ${selectedSeat.id}` });
       fetchSeats();
     } catch (err) { setNotification({ type: 'error', message: 'Checkout Failed.' }); }
     setTimeout(() => setNotification(null), 3000);
  };

  const autoSelectSeat = () => {
    const availableSeats = seats.filter(s => s.status === 'available');
    if (availableSeats.length === 0) {
      setNotification({ type: 'error', message: 'No seats available!' });
      return;
    }
    const randomBest = availableSeats[Math.floor(Math.random() * availableSeats.length)];
    setSelectedSeat(randomBest);
    setNotification({ type: 'success', message: `AI selected Seat #${randomBest.id}` });
  };

  // --- RESTORED: Search Logic (Checks Name OR ID) ---
  const isSearched = (seat) => {
    if (!searchQuery) return false;
    const query = searchQuery.toLowerCase();
    
    // 1. Check Name (if it exists)
    if (seat.user_details && seat.user_details.full_name) {
       if (seat.user_details.full_name.toLowerCase().includes(query)) return true;
    }

    // 2. Check W3 ID / Email
    if (seat.booked_by && seat.booked_by.toLowerCase().includes(query)) {
        return true;
    }
    
    return false;
  };

  const getTimeLeft = (bookingTimeStr) => {
    if (!bookingTimeStr) return "45m 00s";
    const bookedAt = new Date(bookingTimeStr).getTime();
    const expiresAt = bookedAt + (45 * 60 * 1000); // Add 45 mins
    const now = new Date().getTime();
    const diff = expiresAt - now;

    if (diff <= 0) return "Expiring...";
    
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${minutes}m left`;
  };

  const getZoneStyle = (id) => {
    if (id <= 25) return "border-blue-200 bg-blue-50 text-blue-400 hover:border-blue-500 hover:bg-blue-100";
    if (id <= 50) return "border-orange-200 bg-orange-50 text-orange-400 hover:border-orange-500 hover:bg-orange-100";
    if (id <= 75) return "border-red-200 bg-red-50 text-red-400 hover:border-red-500 hover:bg-red-100";
    return "border-green-200 bg-green-50 text-green-400 hover:border-green-500 hover:bg-green-100";
  };

  const FoodStall = ({ name, emoji, color, position, desc }) => (
    <div className={`absolute ${position} flex flex-col items-center z-20 group cursor-help`}>
      <div className={`w-12 h-12 ${color} rounded-full shadow-lg border-4 border-white flex items-center justify-center text-2xl transform transition-transform group-hover:scale-110`}>
        {emoji}
      </div>
      <div className="bg-white px-3 py-1 rounded-full shadow-md border border-stone-200 mt-2 -space-y-0.5 text-center">
        <p className="text-[10px] font-bold uppercase tracking-wider text-stone-800">{name}</p>
        <p className="text-[8px] text-stone-400 font-medium">{desc}</p>
      </div>
    </div>
  );

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-stone-200">
          <h1 className="text-3xl font-serif font-bold text-[#4A403A] text-center mb-2">Blu-Reserve</h1>
          <p className="text-stone-500 mb-8 text-sm text-center">Workplace Capacity Management</p>
          <input type="email" placeholder="w3 ID (e.g. user@in.ibm.com)" className="w-full p-4 border border-stone-200 rounded-xl mb-4 bg-stone-50 text-stone-900 focus:ring-2 focus:ring-[#4A403A] outline-none" value={w3Id} onChange={(e) => setW3Id(e.target.value)} />
          <button onClick={handleLogin} className="w-full bg-[#4A403A] text-white py-4 rounded-xl font-bold shadow-lg hover:bg-[#38302C] transition-all">Sign In with w3</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-100 text-stone-800 font-sans p-4 md:p-8">
      <div className="max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Header */}
        <div className="lg:col-span-12">
          <div className="flex justify-between items-end border-b-2 border-stone-200 pb-6">
            <div>
              <h1 className="text-4xl font-serif font-bold text-[#4A403A]">Blu-Reserve</h1>
              <div className="flex items-center gap-4 mt-2">
                <span className="bg-[#4A403A] text-white text-xs font-bold px-2 py-1 rounded">BLU DOLLAR ENABLED</span>
                <p className="text-stone-400 text-sm font-medium">North Wing • Floor 3</p>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-3">
                 {/* --- RESTORED: Search Input UI --- */}
                 <div className="relative">
                    <input 
                        type="text" 
                        placeholder="Search for a colleague..." 
                        className="pl-9 pr-4 py-2 rounded-full border border-stone-200 bg-white text-sm focus:ring-2 focus:ring-[#4A403A] outline-none w-64 shadow-sm"
                        value={searchQuery} 
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <svg className="absolute left-3 top-2.5 text-stone-400" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </div>

                <div className="flex gap-4">
                  <div className="bg-white p-1 rounded-lg border border-stone-200 shadow-sm flex">
                    {['Today', 'Tomorrow', 'Day After'].map((date) => (
                      <button key={date} onClick={() => setSelectedDate(date)} className={`px-4 py-2 rounded-md text-xs font-bold transition-all ${selectedDate === date ? 'bg-[#4A403A] text-white shadow-md' : 'text-stone-500 hover:bg-stone-100'}`}>{date}</button>
                    ))}
                  </div>
                  <div className="bg-white p-1 rounded-lg border border-stone-200 shadow-sm flex">
                    {['12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM'].map((time) => (
                      <button key={time} onClick={() => setSelectedTime(time)} className={`px-3 py-2 rounded-md text-xs font-bold transition-all ${selectedTime === time ? 'bg-blue-600 text-white shadow-md' : 'text-stone-500 hover:bg-stone-100'}`}>{time}</button>
                    ))}
                  </div>
                </div>
            </div>
          </div>
        </div>

        {/* Map Section */}
        <div className="lg:col-span-9 bg-white rounded-3xl shadow-xl border border-stone-200 p-8 relative overflow-hidden">
           <button onClick={autoSelectSeat} className="absolute top-6 right-6 bg-[#4A403A] text-white px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider hover:bg-[#38302C] transition-all shadow-lg flex items-center gap-2 z-30">
             <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>
             Smart Assign
           </button>

           <div className="mb-10">
             <h2 className="text-xl font-bold text-stone-700 font-serif">Seat Selection</h2>
             <p className="text-stone-400 text-sm">Showing availability for <span className="font-bold text-[#4A403A]">{selectedDate}</span> at <span className="font-bold text-blue-600">{selectedTime}</span></p>
           </div>
           
           <div className="relative bg-stone-50 rounded-[2rem] border-2 border-stone-200 p-16 h-auto min-h-[600px] shadow-inner">
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 bg-white px-6 py-2 border-2 border-stone-200 rounded-lg shadow-md z-20 text-xs font-bold tracking-widest text-stone-400">MAIN ENTRANCE</div>
              <FoodStall position="top-0 left-1/2 transform -translate-x-1/2 -mt-6" name="The Roastery" emoji="☕️" color="bg-blue-100" desc="Cafe & Bakery" />
              <FoodStall position="top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2" name="Fire & Slice" emoji="🍕" color="bg-red-100" desc="Woodfired Pizza" />
              <FoodStall position="top-1/2 left-0 transform -translate-x-1/2 -translate-y-1/2" name="Spice Route" emoji="🍜" color="bg-orange-100" desc="Asian Fusion" />
              <FoodStall position="bottom-0 left-1/2 transform -translate-x-1/2 translate-y-6" name="Green Leaf" emoji="🥗" color="bg-green-100" desc="Salad Bar" />

              <div className="grid grid-cols-10 gap-3">
                {seats.map((seat) => (
                  <button
                    key={seat.id}
                    onClick={() => setSelectedSeat(seat)}
                    className={`
                      aspect-square rounded-lg flex items-center justify-center text-[10px] font-bold transition-all relative shadow-sm border
                      ${isSearched(seat) ? 'bg-yellow-400 text-stone-900 scale-150 z-50 ring-4 ring-yellow-200 shadow-xl' : ''}
                      ${!isSearched(seat) && seat.status === 'occupied' ? 'bg-stone-300 border-stone-300 text-stone-400 opacity-60' : ''}
                      ${!isSearched(seat) && seat.status === 'occupied' && selectedSeat?.id === seat.id ? 'ring-4 ring-[#4A403A] opacity-100 scale-105 z-20' : ''}
                      ${!isSearched(seat) && seat.status === 'available' && selectedSeat?.id === seat.id ? 'bg-[#4A403A] border-[#4A403A] text-white shadow-xl scale-110 z-10' : ''}
                      ${!isSearched(seat) && seat.status === 'available' && selectedSeat?.id !== seat.id ? getZoneStyle(seat.id) : ''}
                    `}
                  >
                    {seat.id}
                  </button>
                ))}
              </div>
           </div>
        </div>

        {/* Right Panel */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-3xl border border-stone-200 p-6 sticky top-8 shadow-xl">
            <div className="flex justify-between items-center mb-6">
               <h2 className="text-lg font-serif font-bold text-[#4A403A]">Booking Summary</h2>
               <div className={`w-2 h-2 rounded-full ${selectedSeat?.status === 'occupied' ? 'bg-red-500' : 'bg-green-500'}`}></div>
            </div>
            
            {selectedSeat ? (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="bg-stone-50 p-4 rounded-2xl border border-stone-100 text-center">
                  <p className="text-xs text-stone-400 uppercase tracking-widest mb-1">Seat Number</p>
                  <p className="text-5xl font-serif font-bold text-[#4A403A]">{selectedSeat.id}</p>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-sm border-b border-stone-100 pb-2">
                    <span className="text-stone-500">Date</span>
                    <span className="font-bold text-[#4A403A]">{selectedDate}</span>
                  </div>
                  
                  {selectedSeat.status === 'occupied' && (
                     <div className="flex justify-between text-sm border-b border-stone-100 pb-2">
                        <span className="text-stone-500">Auto-Checkout In</span>
                        <span className="font-mono font-bold text-red-500">{getTimeLeft(selectedSeat.booking_time)}</span>
                     </div>
                  )}

                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 mt-2">
                     <div className="flex justify-between text-sm mb-1">
                        <span className="text-blue-800 font-bold">Cost</span>
                        <span className="text-blue-800 font-bold">5.00 BD</span>
                     </div>
                     <p className="text-[10px] text-blue-400">Billable to: Manager's Cost Center</p>
                  </div>
                </div>

                {selectedSeat.status === 'available' ? (
                    <button onClick={handleBooking} className="w-full bg-[#4A403A] text-white py-4 rounded-xl font-bold hover:bg-[#2C2826] hover:shadow-lg transition-all transform active:scale-95">
                      Confirm & Charge Manager
                    </button>
                ) : (
                    <button onClick={handleCheckout} className="w-full bg-red-500 text-white py-4 rounded-xl font-bold hover:bg-red-600 transition-all transform active:scale-95">
                       Release Seat
                    </button>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-stone-400 border-2 border-dashed border-stone-100 rounded-2xl">
                 <p className="text-sm italic">"Select a seat."</p>
              </div>
            )}
          </div>
        </div>
      </div>
      {notification && <div className="fixed bottom-10 left-1/2 transform -translate-x-1/2 px-8 py-4 bg-[#2C2826] text-white rounded-full shadow-2xl z-50 font-bold tracking-wide animate-bounce">{notification.message}</div>}
    </div>
  );
};

export default App;