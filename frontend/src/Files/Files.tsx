import { useEffect, useState, type Dispatch, type SetStateAction } from "react";

import { apiFetch } from "../ApiClient";
import ErrorState from "../Ui/ErrorState/ErrorState";
import Page from "../Ui/Layout/Page";
import Stack from "../Ui/Layout/Stack";
import LoadingPage from "../Ui/LoadingPage/LoadingPage";

import MyFilesCard from "./MyFilesCard";

import type { Document } from "../Types/Document";

function Files() {
  const [files, setFiles] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadFilesIntoState(setFiles, setError, setIsLoading);
  }, []);

  const handleRetry = () => {
    setIsLoading(true);
    setError(null);
    void loadFilesIntoState(setFiles, setError, setIsLoading);
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  if (error) {
    return (
      <ErrorState
        title="Couldn't load your files"
        description={error}
        onRetry={handleRetry}
        fullHeight
      />
    );
  }

  return (
    <Page>
      <Stack spacing="md">
        <input type="search" placeholder="Search files" />
        <MyFilesCard files={files} setFiles={setFiles} />
      </Stack>
    </Page>
  );
}

export default Files;

async function loadFilesIntoState(
  setFiles: Dispatch<SetStateAction<Document[]>>,
  setError: Dispatch<SetStateAction<string | null>>,
  setIsLoading: Dispatch<SetStateAction<boolean>>,
): Promise<void> {
  try {
    const files: Document[] = await fetchFiles();
    setFiles(files);
  } catch (error: unknown) {
    setError(
      error instanceof Error
        ? error.message
        : "Failed to get your files. Please try again later.",
    );
  } finally {
    setIsLoading(false);
  }
}

async function fetchFiles(): Promise<Document[]> {
  const response: Response = await apiFetch("/api/documents/", {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error("Failed to get your files. Please try again.");
  }

  const responseJson: { documents: Document[] } = (await response.json()) as {
    documents: Document[];
  };

  return responseJson.documents;
}
