import { useState } from "react";

import { ALLOWED_FILE_TYPES, isFileAllowed } from "./Upload.utils";

import "./Upload.css";

interface UploadResponse {
  files: string[];
}

function Upload() {
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = e.target.files ? Array.from(e.target.files) : [];

    const hasInvalidFile = newFiles.some((file) => {
      if (!isFileAllowed(file)) {
        setError(
          `Only ${ALLOWED_FILE_TYPES.join(", ")} files are supported currently`,
        );
        e.target.value = "";
        return true;
      }
      return false;
    });

    if (hasInvalidFile) {
      return;
    }

    setFiles(newFiles);
  };

  const handleUpload = async () => {
    setError(null);
    setResponseData(null);

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    const response: Response = await fetch("/api/upload/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      setError("Failed to process the files");
      return;
    }

    const responseJson: UploadResponse =
      (await response.json()) as UploadResponse;
    setResponseData(JSON.stringify(responseJson));
  };

  return (
    <>
      <input
        type="file"
        multiple
        accept={ALLOWED_FILE_TYPES.join(",")}
        onChange={handleFileChange}
        onClick={() => {
          setError(null);
          setResponseData(null);
        }}
        aria-label="Upload files"
      />
      <button disabled={files.length === 0} onClick={() => void handleUpload()}>
        Submit for processing
      </button>
      {error && <p>{error}</p>}
      {responseData && <p>{responseData}</p>}
    </>
  );
}

export default Upload;
