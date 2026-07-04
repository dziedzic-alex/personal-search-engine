import {
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";

import { apiFetch } from "../ApiClient";
import { isAbortError } from "../Utils/isAbortError";

import type { Document } from "../Types/Document";
import type {
  FilterConfig,
  SortColumnDirection,
} from "../Types/DocumentsListRequest";
import type { DocumentsListResponse } from "../Types/DocumentsListResponse";

interface UseGetFilesOptions {
  filterConfig: FilterConfig | null;
  query: string | null;
  sortColumnDirection: SortColumnDirection | null;
}

function useGetFiles(options: UseGetFilesOptions) {
  const { filterConfig, query, sortColumnDirection } = options;

  const [files, setFiles] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [nextPage, setNextPage] = useState<number | null>(null);
  const [isFetchingMore, setIsFetchingMore] = useState<boolean>(false);
  const [errorFetchingMore, setErrorFetchingMore] = useState<string | null>(
    null,
  );

  const refetchInitialController = useRef<AbortController | null>(null);
  const fetchMoreController = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    void fetchInitialFiles(
      setFiles,
      setNextPage,
      setIsLoading,
      setError,
      setErrorFetchingMore,
      0,
      filterConfig,
      query,
      sortColumnDirection,
      controller.signal,
    );

    return () => {
      controller.abort();
      refetchInitialController.current?.abort();
      fetchMoreController.current?.abort();
    };
  }, [filterConfig, query, sortColumnDirection]);

  const fetchMoreFiles = async () => {
    if (nextPage === null || isFetchingMore) {
      return;
    }

    fetchMoreController.current?.abort();
    const controller = new AbortController();
    fetchMoreController.current = controller;

    setIsFetchingMore(true);
    setErrorFetchingMore(null);
    try {
      const listFilesResponse: DocumentsListResponse = await fetchDocumentsList(
        nextPage,
        filterConfig,
        query,
        sortColumnDirection,
        controller.signal,
      );

      if (controller !== fetchMoreController.current) {
        return;
      }
      setFiles((prevFiles) => [...prevFiles, ...listFilesResponse.documents]);
      setNextPage(listFilesResponse.nextPage);
    } catch (error: unknown) {
      if (isAbortError(error)) {
        return;
      }

      setErrorFetchingMore(
        error instanceof Error
          ? error.message
          : "Failed to get more files. Please try again.",
      );
    } finally {
      setIsFetchingMore(false);
    }
  };

  const refetchInitialFiles = () => {
    refetchInitialController.current?.abort();
    const controller = new AbortController();
    refetchInitialController.current = controller;

    void fetchInitialFiles(
      setFiles,
      setNextPage,
      setIsLoading,
      setError,
      setErrorFetchingMore,
      0,
      filterConfig,
      query,
      sortColumnDirection,
      controller.signal,
    );
  };

  return {
    files,
    setFiles,
    isLoading,
    error,
    isFetchingMore,
    errorFetchingMore,
    fetchMoreFiles,
    refetchInitialFiles,
  };
}

export default useGetFiles;

async function fetchInitialFiles(
  setFiles: Dispatch<SetStateAction<Document[]>>,
  setNextPage: Dispatch<SetStateAction<number | null>>,
  setIsLoading: Dispatch<SetStateAction<boolean>>,
  setError: Dispatch<SetStateAction<string | null>>,
  setErrorFetchingMore: Dispatch<SetStateAction<string | null>>,
  nextPage: number | null,
  filterConfig: FilterConfig | null,
  query: string | null,
  sortColumnDirection: SortColumnDirection | null,
  signal: AbortSignal,
): Promise<void> {
  setIsLoading(true);
  setError(null);
  setErrorFetchingMore(null);
  try {
    const listFilesResponse: DocumentsListResponse = await fetchDocumentsList(
      nextPage ?? 0,
      filterConfig,
      query,
      sortColumnDirection,
      signal,
    );

    if (signal.aborted) {
      return;
    }

    setFiles(listFilesResponse.documents);
    setNextPage(listFilesResponse.nextPage);
  } catch (error: unknown) {
    if (isAbortError(error)) {
      return;
    }

    setError(
      error instanceof Error
        ? error.message
        : "Failed to get your files. Please try again.",
    );
  }
  setIsLoading(false);
}

async function fetchDocumentsList(
  page: number,
  filterConfig: FilterConfig | null,
  query: string | null,
  sortColumnDirection: SortColumnDirection | null,
  signal: AbortSignal,
): Promise<DocumentsListResponse> {
  const response: Response = await apiFetch("/api/documents/list", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      page: page,
      filterConfig: filterConfig,
      query: query,
      sortConfig: sortColumnDirection,
    }),
    signal: signal,
  });

  if (!response.ok) {
    throw new Error("Failed to get your files. Please try again.");
  }

  return (await response.json()) as DocumentsListResponse;
}
