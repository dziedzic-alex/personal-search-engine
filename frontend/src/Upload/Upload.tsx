import { useState } from "react";

import "./Upload.css";

interface UploadResponse {
  files: string[];
}

const ALLOWED_FILE_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/heic",
  "image/heif",
];

const ALLOWED_FILE_EXTENSIONS = [
  "pdf",
  "jpeg",
  "jpg",
  "png",
  "webp",
  "heic",
  "heif",
];

function Upload() {
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = e.target.files ? Array.from(e.target.files) : [];

    const hasInvalidFile = newFiles.some((file) => {
      if (
        !ALLOWED_FILE_TYPES.includes(file.type) &&
        !ALLOWED_FILE_EXTENSIONS.includes(
          file.name.split(".").pop()?.toLowerCase() ?? "",
        )
      ) {
        console.log(file.type);
        console.log(file.name);
        console.log(file.name.split(".").pop()?.toLowerCase() ?? "");
        setError(
          `Only ${ALLOWED_FILE_TYPES.join(", ")} files are supported currently`,
        );
        e.target.value = "";
        return true;
      }
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
        accept="application/pdf,image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif"
        onChange={handleFileChange}
        onClick={() => {
          setError(null);
          setResponseData(null);
        }}
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
