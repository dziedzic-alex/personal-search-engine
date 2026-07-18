import { useRef, useState, type Dispatch, type SetStateAction } from "react";

import { apiFetch } from "../../ApiClient";
import Button from "../../Ui/Buttons/Button";

import {
  ALLOWED_FILE_TYPES,
  ALLOWED_FILE_EXTENSIONS,
} from "./AllowedFilesConsts";
import UploadingFilesPanel from "./UploadingFilesPanel";

import type { UploadingFile } from "./UploadingFilesPanel";
import type { Document } from "../../Types/Document";

interface Props {
  setFiles: Dispatch<SetStateAction<Document[]>>;
}

function UploadButton(props: Props) {
  const { setFiles } = props;

  const [uploadingFiles, setUploadingFiles] = useState<
    Record<string, UploadingFile>
  >({});

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const clearUploadingFiles = () => {
    setUploadingFiles({});
  };

  const handleUpload = (uploadedFiles: File[]) => {
    const filesToUpload = uploadedFiles.map((file) => ({
      uniqueId: crypto.randomUUID(),
      file,
    }));

    setUploadingFiles((prev) => {
      const newUploadingFiles = { ...prev };
      for (const entry of filesToUpload) {
        newUploadingFiles[entry.uniqueId] = {
          ...entry,
          isUploading: true,
          error: null,
        };
      }
      return newUploadingFiles;
    });

    for (const { uniqueId, file } of filesToUpload) {
      void uploadFile(uniqueId, file);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const uploadFile = async (uniqueId: string, file: File) => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await apiFetch("/api/documents/", {
        method: "POST",
        body: formData,
      });

      if (response.status === 400) {
        throw new Error("File needs a name");
      } else if (response.status === 415) {
        throw new Error(
          `File type not allowed. Only ${ALLOWED_FILE_EXTENSIONS.join(", ")} files are allowed`,
        );
      } else if (response.status === 409) {
        throw new Error(`File ${file.name} already exists`);
      } else if (!response.ok) {
        throw new Error("Error uploading file. Please try again.");
      }

      const newDocument: Document = (await response.json()) as Document;

      setUploadingFiles((prev) => ({
        ...prev,
        [uniqueId]: { file, uniqueId, isUploading: false, error: null },
      }));
      setFiles((prev) => [newDocument, ...prev]);
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Error uploading file. Please try again.";

      setUploadingFiles((prev) => ({
        ...prev,
        [uniqueId]: { file, uniqueId, isUploading: false, error: errorMessage },
      }));
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
          handleUpload(files);
        }}
        aria-label="Upload files"
      />
      <Button size="small" onClick={() => fileInputRef.current?.click()}>
        Upload
      </Button>
      {Object.keys(uploadingFiles).length > 0 && (
        <UploadingFilesPanel
          uploadingFiles={Object.values(uploadingFiles)}
          clearUploadingFiles={clearUploadingFiles}
        />
      )}
    </>
  );
}

export default UploadButton;
