import { EllipsisVertical, Pencil, Eye, Trash, Download } from "lucide-react";
import { useState, type Dispatch, type SetStateAction } from "react";

import { apiFetch } from "../ApiClient";
import ActionMenu from "../Ui/ActionMenu/ActionMenu";
import IconButton from "../Ui/Buttons/IconButton";
import { notify } from "../Ui/Notification/notify";

import FilesTableRenameModal from "./FilesTableRenameModal";

import type { Document } from "../Types/Document";
import type { ActionMenuTriggerProps } from "../Ui/ActionMenu/ActionMenu";

interface Props {
  file: Document;
  setFiles: Dispatch<SetStateAction<Document[]>>;
}

function FilesTableRowActionMenu(props: Props) {
  const { file, setFiles } = props;

  const [renameModalOpen, setRenameModalOpen] = useState<boolean>(false);

  const handleDelete = () => {
    apiFetch(`/api/documents/${file.id.toString()}`, {
      method: "DELETE",
    })
      .then((response: Response) => {
        if (!response.ok) {
          throw new Error("Failed to delete the file. Please try again.");
        }

        setFiles((files) => files.filter((f) => f.id !== file.id));
      })
      .catch((error: unknown) => {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Failed to delete the file. Please try again.";
        notify({ message: errorMessage, variant: "error" });
      });
  };

  return (
    <>
      <ActionMenu
        renderTrigger={(triggerProps: ActionMenuTriggerProps) => (
          <IconButton
            ariaLabel={`Actions for ${file.name}`}
            size="medium"
            {...triggerProps}
          >
            <EllipsisVertical />
          </IconButton>
        )}
        options={[
          {
            id: "rename",
            label: "Rename",
            icon: Pencil,
            onClick: () => {
              setRenameModalOpen(true);
            },
          },
          {
            id: "view",
            label: "View",
            icon: Eye,
            onClick: () => {
              window.open(file.previewUrl, "_blank");
            },
          },
          {
            id: "download",
            label: "Download",
            icon: Download,
            onClick: () => {
              window.location.assign(file.downloadUrl);
            },
          },
          {
            id: "delete",
            label: "Delete",
            icon: Trash,
            variant: "danger",
            onClick: handleDelete,
          },
        ]}
      />
      {renameModalOpen && (
        <FilesTableRenameModal
          onClose={() => {
            setRenameModalOpen(false);
          }}
          file={file}
          setFiles={setFiles}
        />
      )}
    </>
  );
}

export default FilesTableRowActionMenu;
