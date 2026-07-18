import { useState } from "react";

import { useAuth } from "../Auth/AuthContext";
import Button from "../Ui/Buttons/Button";
import Card from "../Ui/Card/Card";
import Stack from "../Ui/Layout/Stack";
import { notify } from "../Ui/Notification/notify";
import TextInput from "../Ui/TextInput/TextInput";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import DeleteAccountConfirmationModal from "./DeleteAccountConfirmationModal";

import "./Account.css";

function Account() {
  const { user, logout, clearSession, updateUser } = useAuth();

  const [firstName, setFirstName] = useState(user.firstName);
  const [lastName, setLastName] = useState(user.lastName);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const [
    isDeleteAccountConfirmationModalOpen,
    setIsDeleteAccountConfirmationModalOpen,
  ] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);

    try {
      await updateUser(firstName, lastName);
      notify({ message: "Account updated successfully.", variant: "success" });
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to update user. Please try again.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } finally {
      setIsLoggingOut(false);
    }
  };

  const fullName = `${user.firstName} ${user.lastName}`;

  return (
    <Card className="account-card">
      <Stack spacing="lg" fullWidth>
        <div>
          <Header>{fullName}</Header>
          <Header level={3}>{user.email}</Header>
        </div>
        <Stack spacing="sm">
          <Stack spacing="sm" direction="horizontal" align="center">
            <div className="account-card-label">
              <Body>First name:</Body>
            </div>
            <TextInput value={firstName} onChange={setFirstName} />
          </Stack>
          <Stack spacing="sm" direction="horizontal" align="center">
            <div className="account-card-label">
              <Body>Last name:</Body>
            </div>
            <TextInput value={lastName} onChange={setLastName} />
          </Stack>
        </Stack>
        <Stack spacing="md" direction="horizontal" align="center">
          <div className="account-card-label">
            <Body>Plan:</Body>
          </div>
          <Body>{user.plan}</Body>
          <Button
            onClick={() => {
              return;
            }}
          >
            Change plan
          </Button>
        </Stack>
        {error && <Body variant="error">{error}</Body>}
        <Button
          onClick={() => void handleSave()}
          isLoading={isSaving}
          loadingText="Saving..."
          isDisabled={
            isSaving ||
            (firstName === user.firstName && lastName === user.lastName)
          }
        >
          Save
        </Button>
        <hr className="account-card-divider" />
        <Stack spacing="sm" direction="horizontal" align="center">
          <Button
            onClick={() => void handleLogout()}
            isLoading={isLoggingOut}
            loadingText="Logging out..."
            variant="secondary"
            fullWidth
          >
            Log out
          </Button>
          <Button
            onClick={() => {
              setIsDeleteAccountConfirmationModalOpen(true);
            }}
            variant="danger"
            fullWidth
          >
            Delete account
          </Button>
        </Stack>
      </Stack>
      {isDeleteAccountConfirmationModalOpen && (
        <DeleteAccountConfirmationModal
          onClose={() => {
            setIsDeleteAccountConfirmationModalOpen(false);
          }}
          clearSession={clearSession}
        />
      )}
    </Card>
  );
}

export default Account;
