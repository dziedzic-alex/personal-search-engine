import { useState } from "react";

import { useAuth } from "../Auth/AuthContext";
import Button from "../Ui/Buttons/Button";
import Card from "../Ui/Card/Card";
import Stack from "../Ui/Layout/Stack";
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
    <Stack spacing="md">
      <Header>Home</Header>
      <Body variant="muted">
        Search across your personal documents and photos.
      </Body>
      <Card>
        <Stack spacing="md">
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
        </Stack>
      </Card>
    </Stack>
  );
}

export default Home;
