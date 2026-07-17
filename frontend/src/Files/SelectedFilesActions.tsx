import { Download, Trash2, X } from "lucide-react";
import { useState } from "react";

import { apiFetch } from "../ApiClient";
import IconButton from "../Ui/Buttons/IconButton";
import Stack from "../Ui/Layout/Stack";
import { notify } from "../Ui/Notification/notify";
import Spinner from "../Ui/Spinner/Spinner";
import Body from "../Ui/Typography/Body";

import type { Document } from "../Types/Document";

import "./SelectedFilesActions.css";

const MAX_BULK_DOWNLOAD_GB = 2;

interface Props {
  selectedFiles: Document[];
  onClearSelectedFiles: () => void;
  handleDelete: () => Promise<void>;
}

function SelectedFilesActions(props: Props) {
  const { selectedFiles, onClearSelectedFiles, handleDelete } = props;

  const [isDownloading, setIsDownloading] = useState(false);

  const selectedCountText =
    selectedFiles.length === 1
      ? "1 file selected"
      : `${String(selectedFiles.length)} files selected`;

  const handleDownload = async () => {
    if (selectedFiles.length === 1) {
      window.location.assign(selectedFiles[0].downloadUrl);
      return;
    }

    setIsDownloading(true);
    notify({
      message: `Zipping ${String(selectedFiles.length)} files...`,
      variant: "info",
    });
    try {
      const response = await apiFetch("/api/documents/bulk-download", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          documentIds: selectedFiles.map((file) => file.id),
        }),
      });

      if (response.status === 400) {
        throw new Error(
          `Total size of selected files exceeds ${String(MAX_BULK_DOWNLOAD_GB)}GB`,
        );
      } else if (!response.ok) {
        throw new Error("Failed to download files. Please try again.");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `personal-search-download-${formatDownloadTimestamp(new Date())}.zip`;
      a.click();
      setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 1000);

      notify({ message: "Files downloaded successfully", variant: "success" });
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Failed to download files. Please try again.";
      notify({ message: errorMessage, variant: "error" });
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="selected-files-actions-container">
      <Stack direction="horizontal" spacing="md" align="center">
        <IconButton
          ariaLabel="Clear selected files"
          onClick={onClearSelectedFiles}
        >
          <X />
        </IconButton>
        <Body>{selectedCountText}</Body>
        <div>
          <IconButton
            ariaLabel="Download selected files"
            onClick={() => void handleDownload()}
          >
            {isDownloading ? <Spinner /> : <Download />}
          </IconButton>
          <IconButton
            ariaLabel="Delete selected files"
            onClick={() => void handleDelete()}
          >
            <Trash2 />
          </IconButton>
        </div>
      </Stack>
    </div>
  );
}

function formatDownloadTimestamp(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");

  return (
    `${String(date.getFullYear())}${pad(date.getMonth() + 1)}${pad(date.getDate())}` +
    `-T${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`
  );
}

export default SelectedFilesActions;
