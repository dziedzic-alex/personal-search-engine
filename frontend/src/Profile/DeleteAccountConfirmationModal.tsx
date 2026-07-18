import { useState } from "react";

import Button from "../Ui/Buttons/Button";
import Stack from "../Ui/Layout/Stack";
import Header from "../Ui/Typography/Header";
import Modal from "../Ui/Modal/Modal";
import Body from "../Ui/Typography/Body";
import { apiFetch } from "../ApiClient";
import { notify } from "../Ui/Notification/notify";

interface Props {
  onClose: () => void;
  clearSession: () => void;
}

function DeleteAccountConfirmationModal(props: Props) {
  const { onClose, clearSession } = props;

  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setIsDeletingAccount(true);
    setError(null);

    try {
      const response = await apiFetch("/api/user/me", {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete account. Please try again.");
      }

      clearSession();
      onClose();
      notify({ message: "Account deleted successfully.", variant: "success" });
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete account. Please try again.",
      );
    } finally {
      setIsDeletingAccount(false);
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      ariaLabel="Delete account confirmation"
    >
      <Header>Delete account</Header>
      <Stack spacing="sm">
        <Body>
          Are you sure you want to delete your account? This action is
          irreversible.
        </Body>
        {error && <Body variant="error">{error}</Body>}
        <Stack spacing="sm" direction="horizontal" align="center" justify="end">
          <Button onClick={onClose} variant="secondary">
            Cancel
          </Button>
          <Button
            onClick={() => void handleDelete()}
            isDisabled={isDeletingAccount}
            isLoading={isDeletingAccount}
            loadingText="Deleting account..."
            variant="danger"
          >
            Delete account
          </Button>
        </Stack>
      </Stack>
    </Modal>
  );
}

export default DeleteAccountConfirmationModal;
