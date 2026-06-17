import { useState } from "react";

import { useAuth } from "../Auth/AuthContext";

import "./Home.css";

function Home() {
  const { logout } = useAuth();

  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    await logout();
    setIsLoggingOut(false);
  };

  return (
    <div className="home">
      <h1 className="home-title">Home</h1>
      <p className="home-description">
        Search across your personal documents and photos.
      </p>
      <div className="home-card">
        <p className="home-card-text">
          Upload files to index them, then search by natural language from the
          Search page.
        </p>
        <button
          className="home-logout-button"
          onClick={() => void handleLogout()}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Logging out..." : "Log out"}
        </button>
      </div>
    </div>
  );
}

export default Home;
