import { useRef, useState, type Dispatch, type SetStateAction } from "react";

import { apiFetch } from "../ApiClient";
import Button from "../Ui/Buttons/Button";
import { notify } from "../Ui/Notification/notify";

import { ALLOWED_FILE_TYPES, isFileAllowed } from "./uploadButton.utils";

import type { Document } from "../Types/Document";

interface UploadResponse {
  filesBeingProcessed: Document[];
  errors: string[];
}

interface Props {
  setFiles: Dispatch<SetStateAction<Document[]>>;
}

function UploadButton(props: Props) {
  const { setFiles } = props;

  const [isUploading, setIsUploading] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const hasInvalidFile = (files: File[]) => {
    return files.some((file) => {
      if (!isFileAllowed(file)) {
        const errorMessage = `Only ${ALLOWED_FILE_TYPES.join(", ")} files are supported currently`;
        notify({ message: errorMessage, variant: "error" });
        return true;
      }
      return false;
    });
  };

  const handleUpload = async (uploadedFiles: File[]) => {
    setIsUploading(true);
    const formData = new FormData();

    uploadedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response: Response = await apiFetch("/api/upload/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          `Failed to upload the file${uploadedFiles.length > 1 ? "s" : ""}`,
        );
      }

      const responseJson: UploadResponse =
        (await response.json()) as UploadResponse;

      setFiles((files) => [...files, ...responseJson.filesBeingProcessed]);

      if (responseJson.errors.length > 0) {
        const errorMessage = `Only ${responseJson.filesBeingProcessed.length.toString()} of ${uploadedFiles.length.toString()} files were uploaded. Reasons: ${responseJson.errors.join(", ")}`;
        notify({ message: errorMessage, variant: "error" });
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : `Failed to upload the file${uploadedFiles.length > 1 ? "s" : ""}`;
      notify({ message: errorMessage, variant: "error" });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <>
      <input
        ref={fileInputRef}
        hidden
        type="file"
        multiple
        accept={ALLOWED_FILE_TYPES.join(",")}
        onChange={(e) => {
          const files = e.target.files ? Array.from(e.target.files) : [];

          if (hasInvalidFile(files)) {
            return;
          }

          void handleUpload(files);
        }}
        aria-label="Upload files"
      />
      <Button
        isLoading={isUploading}
        loadingText="Uploading..."
        size="small"
        onClick={() => fileInputRef.current?.click()}
      >
        Upload
      </Button>
    </>
  );
}

export default UploadButton;
