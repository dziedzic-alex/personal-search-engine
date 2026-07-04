import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { makeDocument } from "./filesTest.utils";
import useGetFiles from "./useGetFiles";

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

describe("useGetFiles", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
  });

  it("fetches the first page on mount", async () => {
    const files = [
      makeDocument({ id: 1, name: "report.pdf" }),
      makeDocument({ id: 2, name: "photo.jpg", contentCategory: "image" }),
    ];
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ documents: files, nextPage: null }),
    } as Response);

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
    const page0 = [makeDocument({ id: 1, name: "report.pdf" })];
    const page1 = [
      makeDocument({ id: 2, name: "photo.jpg", contentCategory: "image" }),
    ];
    mockApiFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ documents: page0, nextPage: 1 }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ documents: page1, nextPage: null }),
      } as Response);

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
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ documents: [], nextPage: null }),
    } as Response);

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
});
