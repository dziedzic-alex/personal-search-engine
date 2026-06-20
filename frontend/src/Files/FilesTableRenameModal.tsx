import { useState } from "react";

import { apiFetch } from "../ApiClient";
import Button from "../Ui/Button";
import Stack from "../Ui/Layout/Stack";
import Modal from "../Ui/Modal/Modal";
import TextInput from "../Ui/TextInput/TextInput";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import type { Document } from "../Types/Document";
import type { Dispatch, SetStateAction } from "react";

interface Props {
  onClose: () => void;
  file: Document;
  setFiles: Dispatch<SetStateAction<Document[]>>;
}

function FilesTableRenameModal(props: Props) {
  const { onClose, file, setFiles } = props;

  const [renameModalNewName, setRenameModalNewName] = useState<string>(
    file.name,
  );
  const [isSavingRename, setIsSavingRename] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRename = () => {
    setIsSavingRename(true);
    setError(null);
    apiFetch(`/api/documents/${file.id.toString()}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: renameModalNewName }),
    })
      .then((response: Response) => {
        if (!response.ok) {
          throw new Error("Failed to rename the file. Please try again later.");
        }

        return response.json();
      })
      .then((data: Document) => {
        setFiles((files) => files.map((f) => (f.id === data.id ? data : f)));
        onClose();
      })
      .catch((error: unknown) => {
        setError(
          error instanceof Error
            ? error.message
            : "Failed to rename the file. Please try again later.",
        );
      })
      .finally(() => {
        setIsSavingRename(false);
      });
  };

  return (
    <Modal isOpen={true} onClose={onClose} ariaLabel="Rename file">
      <Stack spacing="md">
        <Header level={2}>Rename</Header>
        <TextInput
          value={renameModalNewName}
          onChange={(value) => {
            setRenameModalNewName(value);
            setError(null);
          }}
          name="renameModalNameInput"
          placeholder="Enter new name"
          autoFocus
        />
        {error ? <Body variant="error">{error}</Body> : null}
        <Stack direction="horizontal" spacing="sm" justify="end">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            isDisabled={
              renameModalNewName.trim() === "" ||
              renameModalNewName === file.name
            }
            isLoading={isSavingRename}
            loadingText="Saving..."
            onClick={handleRename}
          >
            Save
          </Button>
        </Stack>
      </Stack>
    </Modal>
  );
}

export default FilesTableRenameModal;
