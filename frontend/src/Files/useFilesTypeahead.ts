import { useEffect, useState } from "react";

import { apiFetch } from "../ApiClient";
import { isAbortError } from "../Utils/isAbortError";

import type { Document } from "../Types/Document";

function useFilesTypeahead(query: string) {
  const [files, setFiles] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasCompletedFirstFetch, setHasCompletedFirstFetch] =
    useState<boolean>(false);

  const hasQuery = query.length > 0;

  useEffect(() => {
    if (!hasQuery) {
      resetState(setFiles, setIsLoading, setError, setHasCompletedFirstFetch);
      return;
    }

    const controller = new AbortController();

    void fetchTypeaheadFiles(
      query,
      controller.signal,
      setFiles,
      setIsLoading,
      setError,
      setHasCompletedFirstFetch,
    );

    return () => {
      controller.abort();
    };
  }, [hasQuery, query]);

  return {
    files: hasQuery ? files : [],
    isLoading: hasQuery ? isLoading : false,
    error: hasQuery ? error : null,
    hasCompletedFirstFetch: hasQuery ? hasCompletedFirstFetch : false,
  };
}

export default useFilesTypeahead;

function resetState(
  setFiles: (files: Document[]) => void,
  setIsLoading: (isLoading: boolean) => void,
  setError: (error: string | null) => void,
  setHasCompletedFirstFetch: (hasCompletedFirstFetch: boolean) => void,
) {
  setFiles([]);
  setIsLoading(false);
  setError(null);
  setHasCompletedFirstFetch(false);
}

async function fetchTypeaheadFiles(
  query: string,
  signal: AbortSignal,
  setFiles: (files: Document[]) => void,
  setIsLoading: (isLoading: boolean) => void,
  setError: (error: string | null) => void,
  setHasCompletedFirstFetch: (hasCompletedFirstFetch: boolean) => void,
): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const documents = await fetchDocumentSuggestions(query, signal);

    if (signal.aborted) {
      return;
    }

    setFiles(documents);
  } catch (fetchError: unknown) {
    if (isAbortError(fetchError)) {
      return;
    }

    setError(
      fetchError instanceof Error
        ? fetchError.message
        : "Failed to search. Please try again.",
    );
  }
  setHasCompletedFirstFetch(true);
  setIsLoading(false);
}

async function fetchDocumentSuggestions(
  query: string,
  signal: AbortSignal,
): Promise<Document[]> {
  const response: Response = await apiFetch(
    `/api/documents/suggest?query=${encodeURIComponent(query)}`,
    {
      method: "GET",
      signal: signal,
    },
  );

  if (!response.ok) {
    throw new Error("Failed to search. Please try again.");
  }

  return (await response.json()) as Document[];
}
