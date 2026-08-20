import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { makeDocument } from "./filesTest.utils";
import useGetFiles from "./useGetFiles";

import type { Document } from "../Types/Document";

const mockApiFetch =
  vi.fn<(url: string, options?: RequestInit) => Promise<Response>>();

vi.mock("../ApiClient", () => ({
  apiFetch: (url: string, options?: RequestInit) => mockApiFetch(url, options),
}));

const defaultProps = {
  filterConfig: null,
  query: null,
  sortColumnDirection: null,
};

function mockListResponse(
  documents: Document[],
  nextPage: number | null = null,
) {
  return {
    ok: true,
    json: () => Promise.resolve({ documents, nextPage }),
  } as Response;
}

function mockByIdsResponse(documents: Document[]) {
  return {
    ok: true,
    json: () => Promise.resolve(documents),
  } as Response;
}

async function flushPromises() {
  await act(async () => {
    await Promise.resolve();
  });
}

describe("useGetFiles", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
  });

  it("fetches the first page on mount", async () => {
    const files = [
      makeDocument({ id: "1", name: "report.pdf" }),
      makeDocument({ id: "2", name: "photo.jpg", contentCategory: "image" }),
    ];
    mockApiFetch.mockResolvedValue(mockListResponse(files));

    const { result } = renderHook(() => useGetFiles(defaultProps));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockApiFetch).toHaveBeenCalledWith(
      "/api/documents/list",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          page: 0,
          filterConfig: null,
          query: null,
          sortConfig: null,
        }),
      }),
    );
    expect(result.current.files).toEqual(files);
    expect(result.current.error).toBeNull();
  });

  it("fetchMoreFiles appends the next page", async () => {
    const page0 = [makeDocument({ id: "1", name: "report.pdf" })];
    const page1 = [
      makeDocument({ id: "2", name: "photo.jpg", contentCategory: "image" }),
    ];
    mockApiFetch
      .mockResolvedValueOnce(mockListResponse(page0, 1))
      .mockResolvedValueOnce(mockListResponse(page1));

    const { result } = renderHook(() => useGetFiles(defaultProps));

    await waitFor(() => {
      expect(result.current.files).toEqual(page0);
    });

    await act(async () => {
      await result.current.fetchMoreFiles();
    });

    expect(mockApiFetch).toHaveBeenCalledTimes(2);
    expect(JSON.parse(mockApiFetch.mock.calls[1][1]?.body as string)).toEqual({
      page: 1,
      filterConfig: null,
      query: null,
      sortConfig: null,
    });
    expect(result.current.files).toEqual([...page0, ...page1]);
    expect(result.current.errorFetchingMore).toBeNull();
  });

  it("does not fetch more when there is no next page", async () => {
    mockApiFetch.mockResolvedValue(mockListResponse([]));

    const { result } = renderHook(() => useGetFiles(defaultProps));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.fetchMoreFiles();
    });

    expect(mockApiFetch).toHaveBeenCalledTimes(1);
  });

  it("sets an error when the initial request fails", async () => {
    mockApiFetch.mockResolvedValue({
      ok: false,
    } as Response);

    const { result } = renderHook(() => useGetFiles(defaultProps));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.files).toEqual([]);
    expect(result.current.error).toBe(
      "Failed to get your files. Please try again.",
    );
  });

  describe("status polling", () => {
    beforeEach(() => {
      vi.useFakeTimers({ toFake: ["setInterval", "clearInterval"] });
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    async function advancePollInterval() {
      await act(async () => {
        await vi.advanceTimersByTimeAsync(30_000);
      });
    }

    it("does not poll when all files are processed", async () => {
      const files = [
        makeDocument({ id: "1", status: "processed" }),
        makeDocument({ id: "2", status: "processed" }),
      ];
      mockApiFetch.mockResolvedValue(mockListResponse(files));

      const { result } = renderHook(() => useGetFiles(defaultProps));

      await flushPromises();
      expect(result.current.files).toEqual(files);

      await advancePollInterval();

      expect(
        mockApiFetch.mock.calls.some(
          ([url]) => url === "/api/documents/by-ids",
        ),
      ).toBe(false);
    });

    it("polls by-ids and merges updated statuses", async () => {
      const pendingFile = makeDocument({
        id: "2",
        name: "uploading.pdf",
        status: "pending",
      });
      const processedFile = makeDocument({
        id: "1",
        name: "done.pdf",
        status: "processed",
      });
      const updatedPendingFile = makeDocument({
        id: "2",
        name: "uploading.pdf",
        status: "processed",
      });

      mockApiFetch.mockImplementation((url) => {
        if (url === "/api/documents/list") {
          return Promise.resolve(
            mockListResponse([pendingFile, processedFile]),
          );
        }
        if (url === "/api/documents/by-ids") {
          return Promise.resolve(mockByIdsResponse([updatedPendingFile]));
        }
        return Promise.reject(new Error(`Unexpected url: ${url}`));
      });

      const { result } = renderHook(() => useGetFiles(defaultProps));

      await flushPromises();
      expect(result.current.files).toEqual([pendingFile, processedFile]);

      await advancePollInterval();
      await flushPromises();

      expect(result.current.files).toEqual([updatedPendingFile, processedFile]);

      const byIdsCall = mockApiFetch.mock.calls.find(
        ([url]) => url === "/api/documents/by-ids",
      );
      expect(byIdsCall).toBeDefined();
      expect(JSON.parse(byIdsCall?.[1]?.body as string)).toEqual({
        documentIds: ["2"],
      });
    });

    it("polls pending and processing ids together", async () => {
      const processingFile = makeDocument({ id: "3", status: "processing" });
      const processedFile = makeDocument({ id: "1", status: "processed" });
      const pendingFile = makeDocument({ id: "2", status: "pending" });
      mockApiFetch.mockImplementation((url) => {
        if (url === "/api/documents/list") {
          return Promise.resolve(
            mockListResponse([processingFile, processedFile, pendingFile]),
          );
        }
        if (url === "/api/documents/by-ids") {
          return Promise.resolve(
            mockByIdsResponse([pendingFile, processingFile]),
          );
        }
        return Promise.reject(new Error(`Unexpected url: ${url}`));
      });

      const { result } = renderHook(() => useGetFiles(defaultProps));

      await flushPromises();
      expect(result.current.isLoading).toBe(false);

      await advancePollInterval();
      await flushPromises();

      const byIdsCall = mockApiFetch.mock.calls.find(
        ([url]) => url === "/api/documents/by-ids",
      );
      expect(JSON.parse(byIdsCall?.[1]?.body as string)).toEqual({
        documentIds: ["2", "3"],
      });
    });

    it("aborts in-flight poll requests on unmount", async () => {
      const pendingFile = makeDocument({ id: "1", status: "pending" });
      let pollSignal: AbortSignal | undefined;

      mockApiFetch.mockImplementation((url, options) => {
        if (url === "/api/documents/list") {
          return Promise.resolve(mockListResponse([pendingFile]));
        }
        if (url === "/api/documents/by-ids") {
          pollSignal = options?.signal ?? undefined;
          return new Promise(() => {
            // Keep the poll request pending until unmount aborts it.
          });
        }
        return Promise.reject(new Error(`Unexpected url: ${url}`));
      });

      const { result, unmount } = renderHook(() => useGetFiles(defaultProps));

      await flushPromises();
      expect(result.current.files).toEqual([pendingFile]);

      await advancePollInterval();
      await flushPromises();
      expect(pollSignal).toBeDefined();

      unmount();

      expect(pollSignal?.aborted).toBe(true);
    });

    it("stops polling once all files are processed", async () => {
      const pendingFile = makeDocument({ id: "1", status: "pending" });
      const processedFile = makeDocument({ id: "1", status: "processed" });
      const pollSignals: AbortSignal[] = [];

      mockApiFetch.mockImplementation((url, options) => {
        if (url === "/api/documents/list") {
          return Promise.resolve(mockListResponse([pendingFile]));
        }
        if (url === "/api/documents/by-ids") {
          if (options?.signal) {
            pollSignals.push(options.signal);
          }
          return Promise.resolve(mockByIdsResponse([processedFile]));
        }
        return Promise.reject(new Error(`Unexpected url: ${url}`));
      });

      const { result } = renderHook(() => useGetFiles(defaultProps));

      await flushPromises();
      expect(result.current.files[0]?.status).toBe("pending");

      await advancePollInterval();
      await flushPromises();

      expect(result.current.files[0]?.status).toBe("processed");
      expect(pollSignals[0]?.aborted).toBe(true);

      await advancePollInterval();
      await flushPromises();

      expect(
        mockApiFetch.mock.calls.filter(
          ([url]) => url === "/api/documents/by-ids",
        ),
      ).toHaveLength(1);
    });
  });
});
