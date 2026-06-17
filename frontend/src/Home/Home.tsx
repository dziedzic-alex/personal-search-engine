import { useState } from "react";

import { useAuth } from "../Auth/AuthContext";
import Button from "../Ui/Button";
import Card from "../Ui/Card";
import Page from "../Ui/Layout/Page";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";


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
        <Button
          onClick={() => void handleLogout()}
          isLoading={isLoggingOut}
          loadingText="Logging out..."
        >
          Log out
        </Button>
      </Card>
    </Page>
  );
}

export default Home;
