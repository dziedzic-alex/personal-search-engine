import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { makeDocument } from "./filesTest.utils";
import useFilesTypeahead from "./useFilesTypeahead";

const mockApiFetch =
  vi.fn<(url: string, options?: RequestInit) => Promise<Response>>();

vi.mock("../ApiClient", () => ({
  apiFetch: (url: string, options?: RequestInit) => mockApiFetch(url, options),
}));

describe("useFilesTypeahead", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
  });

  it("does not fetch when the query is empty", () => {
    const { result } = renderHook(() => useFilesTypeahead(""));

    expect(mockApiFetch).not.toHaveBeenCalled();
    expect(result.current.files).toEqual([]);
    expect(result.current.error).toBeNull();
    expect(result.current.hasCompletedFirstFetch).toBe(false);
    expect(result.current.isLoading).toBe(false);
  });

  it("fetches suggestions when the query is set", async () => {
    const files = [
      makeDocument({ id: 1, name: "report.pdf" }),
      makeDocument({ id: 2, name: "annual-report.pdf" }),
    ];
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(files),
    } as Response);

    const { result } = renderHook(() => useFilesTypeahead("rep"));

    await waitFor(() => {
      expect(result.current.hasCompletedFirstFetch).toBe(true);
    });

    expect(mockApiFetch).toHaveBeenCalledWith(
      "/api/documents/suggest?query=rep",
      expect.objectContaining({ method: "GET" }),
    );
    expect(mockApiFetch.mock.calls[0][1]?.signal).toBeInstanceOf(AbortSignal);
    expect(result.current.files).toEqual(files);
    expect(result.current.error).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it("aborts the prior request when the query changes", async () => {
    let firstSignal: AbortSignal | undefined;
    let resolveFirstRequest: (value: Response) => void;

    mockApiFetch.mockImplementation((_url, options) => {
      if (!firstSignal) {
        const signal = options?.signal;
        if (!signal) {
          throw new Error("expected abort signal");
        }
        firstSignal = signal;
        return new Promise<Response>((resolve) => {
          resolveFirstRequest = resolve;
        });
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);
    });

    const { rerender } = renderHook(({ query }) => useFilesTypeahead(query), {
      initialProps: { query: "rep" },
    });

    rerender({ query: "repo" });

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledTimes(2);
    });

    expect(firstSignal?.aborted).toBe(true);

    resolveFirstRequest({
      ok: true,
      json: () => Promise.resolve([makeDocument()]),
    } as Response);
  });

  it("sets an error when the request fails", async () => {
    mockApiFetch.mockResolvedValue({
      ok: false,
    } as Response);

    const { result } = renderHook(() => useFilesTypeahead("broken"));

    await waitFor(() => {
      expect(result.current.hasCompletedFirstFetch).toBe(true);
    });

    expect(result.current.files).toEqual([]);
    expect(result.current.error).toBe("Failed to search. Please try again.");
    expect(result.current.isLoading).toBe(false);
  });

  it("resets state when the query is cleared", async () => {
    const files = [makeDocument({ id: 1, name: "report.pdf" })];
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(files),
    } as Response);

    const { result, rerender } = renderHook(
      ({ query }) => useFilesTypeahead(query),
      { initialProps: { query: "rep" } },
    );

    await waitFor(() => {
      expect(result.current.files).toEqual(files);
    });

    rerender({ query: "" });

    expect(mockApiFetch).toHaveBeenCalledTimes(1);
    expect(result.current.files).toEqual([]);
    expect(result.current.error).toBeNull();
    expect(result.current.hasCompletedFirstFetch).toBe(false);
    expect(result.current.isLoading).toBe(false);
  });
});
