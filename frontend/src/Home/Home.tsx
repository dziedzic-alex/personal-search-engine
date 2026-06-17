import { useState } from "react";

import { useAuth } from "../Auth/AuthContext";
import Card from "../Ui/Card";
import Page from "../Ui/Layout/Page";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

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
    <Page>
      <Header>Home</Header>
      <Body variant="muted">
        Search across your personal documents and photos.
      </Body>
      <Card>
        <Body variant="muted">
          Upload files to index them, then search by natural language from the
          Search page.
        </Body>
        <button
          className="home-logout-button"
          onClick={() => void handleLogout()}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Logging out..." : "Log out"}
        </button>
      </Card>
    </Page>
  );
}

export default Home;
