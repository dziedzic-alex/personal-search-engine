import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiFetch, configureApiClient } from "./ApiClient";

function mockResponse(status: number, body = ""): Response {
  return new Response(body, { status });
}

describe("apiFetch", () => {
  const getAccessToken = vi.fn<() => string | null>();
  const refreshAccessToken = vi.fn<() => Promise<void>>();
  const clearSession = vi.fn<() => void>();
  const navigateToLogin = vi.fn<() => void>();
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    configureApiClient({
      getAccessToken,
      refreshAccessToken,
      clearSession,
      navigateToLogin,
    });
    getAccessToken.mockReset();
    refreshAccessToken.mockReset();
    clearSession.mockReset();
    navigateToLogin.mockReset();
    fetchMock.mockReset();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("adds Bearer header when access token exists", async () => {
    getAccessToken.mockReturnValue("token-a");
    fetchMock.mockResolvedValue(mockResponse(200));

    await apiFetch("/api/search");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const requestOptions = fetchMock.mock.calls[0]?.[1];
    const headers = requestOptions?.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer token-a");
  });

  it("returns response on success without refreshing", async () => {
    getAccessToken.mockReturnValue("token-a");
    const successResponse = mockResponse(200, "ok");
    fetchMock.mockResolvedValue(successResponse);

    const response = await apiFetch("/api/search");

    expect(response).toBe(successResponse);
    expect(refreshAccessToken).not.toHaveBeenCalled();
  });

  it("refreshes and retries on 401 with updated token", async () => {
    getAccessToken.mockReturnValueOnce("token-a").mockReturnValue("token-b");
    fetchMock
      .mockResolvedValueOnce(mockResponse(401))
      .mockResolvedValueOnce(mockResponse(200, "ok"));
    refreshAccessToken.mockResolvedValue();

    const response = await apiFetch("/api/search");

    expect(refreshAccessToken).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);

    const retryOptions = fetchMock.mock.calls[1]?.[1];
    const retryHeaders = retryOptions?.headers as Headers;
    expect(retryHeaders.get("Authorization")).toBe("Bearer token-b");
    expect(response.status).toBe(200);
  });

  it("refreshes and retries on 403", async () => {
    getAccessToken.mockReturnValueOnce("token-a").mockReturnValue("token-b");
    fetchMock
      .mockResolvedValueOnce(mockResponse(403))
      .mockResolvedValueOnce(mockResponse(200));
    refreshAccessToken.mockResolvedValue();

    const response = await apiFetch("/api/upload");

    expect(refreshAccessToken).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(response.status).toBe(200);
  });

  it("clears session and navigates to login when retry still fails", async () => {
    getAccessToken.mockReturnValue("token-a");
    fetchMock
      .mockResolvedValueOnce(mockResponse(401))
      .mockResolvedValueOnce(mockResponse(401));
    refreshAccessToken.mockResolvedValue();

    await expect(apiFetch("/api/search")).rejects.toThrow("Unauthorized");

    expect(clearSession).toHaveBeenCalledTimes(1);
    expect(navigateToLogin).toHaveBeenCalledTimes(1);
  });

  it("rethrows Error instances from fetch", async () => {
    getAccessToken.mockReturnValue(null);
    fetchMock.mockRejectedValue(new Error("network error"));

    await expect(apiFetch("/api/search")).rejects.toThrow("network error");
    expect(refreshAccessToken).not.toHaveBeenCalled();
  });

  it("wraps non-Error throws as Request failed", async () => {
    getAccessToken.mockReturnValue(null);
    fetchMock.mockRejectedValue("boom");

    await expect(apiFetch("/api/search")).rejects.toThrow("Request failed");
  });
});
