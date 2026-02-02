import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import axios from "axios";
import './index.css';
import App from "./App";
import Login from "./login";

const Root = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/seats", { withCredentials: true })
      .then(() => setIsLoggedIn(true))
      .catch(() => setIsLoggedIn(false));
  }, []);

  if (isLoggedIn === null) return null; // or loading spinner later

  return isLoggedIn ? <App /> : <Login />;
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);