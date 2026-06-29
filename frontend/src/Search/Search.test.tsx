import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { makeDocument } from "../Files/filesTest.utils";

import Search from "./Search";

const mockApiFetch =
  vi.fn<(url: string, options?: RequestInit) => Promise<Response>>();

vi.mock("../ApiClient", () => ({
  apiFetch: (url: string, options?: RequestInit) => mockApiFetch(url, options),
}));

function renderSearch() {
  return render(
    <MemoryRouter>
      <Search />
    </MemoryRouter>,
  );
}

describe("Search", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
  });

  it("does not search when the query is empty", async () => {
    renderSearch();

    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(mockApiFetch).not.toHaveBeenCalled();
  });

  it("searches documents and renders results", async () => {
    const files = [
      makeDocument({ id: 1, name: "contract.pdf" }),
      makeDocument({ id: 2, name: "photo.jpg", contentCategory: "image" }),
    ];
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(files),
    } as Response);

    renderSearch();

    await userEvent.type(screen.getByPlaceholderText("Search"), "contract");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith(
        "/api/documents/search?query=contract&search_mode=text",
        { method: "GET" },
      );
    });

    expect(screen.getByText("contract.pdf")).toBeInTheDocument();
    expect(screen.getByText("photo.jpg")).toBeInTheDocument();
  });

  it("includes the selected search mode in the request", async () => {
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    } as Response);

    renderSearch();

    await userEvent.click(screen.getByRole("radio", { name: "Images" }));
    await userEvent.type(screen.getByPlaceholderText("Search"), "sunset");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith(
        "/api/documents/search?query=sunset&search_mode=image",
        { method: "GET" },
      );
    });
  });

  it("shows an empty state when search returns no results", async () => {
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    } as Response);

    renderSearch();

    await userEvent.type(screen.getByPlaceholderText("Search"), "missing");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(
      await screen.findByRole("heading", { name: "No processed files" }),
    ).toBeInTheDocument();
  });

  it("shows an error when search fails", async () => {
    mockApiFetch.mockResolvedValue({
      ok: false,
    } as Response);

    renderSearch();

    await userEvent.type(screen.getByPlaceholderText("Search"), "broken");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(await screen.findByText("Failed to search")).toBeInTheDocument();
  });
});
