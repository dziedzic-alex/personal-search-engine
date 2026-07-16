import { useState, type Dispatch, type SetStateAction } from "react";

import { apiFetch } from "../ApiClient";
import Button from "../Ui/Buttons/Button";
import Stack from "../Ui/Layout/Stack";
import Modal from "../Ui/Modal/Modal";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import type { Document } from "../Types/Document";

import "./FilesTableBulkDeleteModal.css";

interface Props {
  selectedFiles: Document[];
  clearSelectedFiles: () => void;
  onClose: () => void;
  setFiles: Dispatch<SetStateAction<Document[]>>;
}

function FilesTableBulkDeleteModal(props: Props) {
  const { selectedFiles, clearSelectedFiles, onClose, setFiles } = props;

  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onConfirmDelete = async () => {
    setIsDeleting(true);
    setError(null);

    try {
      const selectedFileIds = selectedFiles.map((file) => file.id);

      const response = await apiFetch(`/api/documents/bulk-delete`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          documentIds: selectedFileIds,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to delete the files. Please try again.");
      }

      setFiles((files) =>
        files.filter((file) => !selectedFileIds.includes(file.id)),
      );
      clearSelectedFiles();
      onClose();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete the files. Please try again.",
      );
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Modal isOpen={true} onClose={onClose} ariaLabel="Delete selected files">
      <Stack spacing="md" className="files-table-bulk-delete-modal-content">
        <Header level={2}>Delete files</Header>
        <Body>{`Are you sure you want to delete ${String(selectedFiles.length)} files?`}</Body>
        {error ? <Body variant="error">{error}</Body> : null}
        <Stack direction="horizontal" spacing="sm" justify="end">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            isLoading={isDeleting}
            loadingText="Deleting..."
            onClick={() => void onConfirmDelete()}
          >
            Delete
          </Button>
        </Stack>
      </Stack>
    </Modal>
  );
}

export default FilesTableBulkDeleteModal;
