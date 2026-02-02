// src/login.jsx
import React from "react";

const Login = () => {
  const handleLogin = () => {
    window.location.href = "http://127.0.0.1:8000/auth/login";
  };

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
};

export default Login;
