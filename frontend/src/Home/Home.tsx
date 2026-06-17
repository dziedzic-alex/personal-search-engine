import { useState } from "react";

import { useAuth } from "../Auth/AuthContext";

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
      Home
      <button onClick={() => void handleLogout()} disabled={isLoggingOut}>
        {isLoggingOut ? "Logging out..." : "Log out"}
      </button>
    </div>
  );
}

export default Home;
