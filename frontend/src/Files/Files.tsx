import { useEffect, useState, type Dispatch, type SetStateAction } from "react";

import { apiFetch } from "../ApiClient";
import ErrorState from "../Ui/ErrorState/ErrorState";
import Stack from "../Ui/Layout/Stack";
import SearchBar from "../Ui/SearchBar/SearchBar";

import MyFilesCard from "./MyFilesCard";

import type { Document } from "../Types/Document";

import "./Files.css";

function Files() {
  const [files, setFiles] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [hasMadeSearchQuery, setHasMadeSearchQuery] = useState<boolean>(false);

  useEffect(() => {
    void loadFilesIntoState(setFiles, setError, setIsLoading);
  }, []);

  const refetchFiles = () => {
    setHasMadeSearchQuery(searchQuery.length > 0);
    setIsLoading(true);
    setError(null);
    void loadFilesIntoState(setFiles, setError, setIsLoading, searchQuery);
  };

  const clearSearch = () => {
    setSearchQuery("");
    setHasMadeSearchQuery(false);
    setIsLoading(true);
    setError(null);
    void loadFilesIntoState(setFiles, setError, setIsLoading);
  };

  if (error) {
    return (
      <ErrorState
        title="Couldn't load your files"
        description={error}
        onRetry={refetchFiles}
        fullHeight
      />
    );
  }

  return (
    <Stack spacing="md" className="files-container">
      <SearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={refetchFiles}
        placeholder="Search by file name"
        isDisabled={isLoading || (files.length === 0 && !hasMadeSearchQuery)}
      />
      <MyFilesCard
        files={files}
        setFiles={setFiles}
        isLoadingFiles={isLoading}
        hasMadeSearchQuery={hasMadeSearchQuery}
        clearSearch={clearSearch}
      />
    </Stack>
  );
}

export default Files;

async function loadFilesIntoState(
  setFiles: Dispatch<SetStateAction<Document[]>>,
  setError: Dispatch<SetStateAction<string | null>>,
  setIsLoading: Dispatch<SetStateAction<boolean>>,
  query?: string,
): Promise<void> {
  try {
    const files: Document[] = await fetchFiles(query);
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

async function fetchFiles(searchQuery?: string): Promise<Document[]> {
  let url = "/api/documents/";
  if (searchQuery) {
    url += `?query=${encodeURIComponent(searchQuery)}`;
  }

  const response: Response = await apiFetch(url, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error("Failed to get your files. Please try again.");
  }

  const responseJson = (await response.json()) as Document[];

  return responseJson;
}
