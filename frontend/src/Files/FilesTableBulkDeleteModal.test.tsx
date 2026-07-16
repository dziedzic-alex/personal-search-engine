import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import FilesTableBulkDeleteModal from "./FilesTableBulkDeleteModal";
import { makeDocument } from "./filesTest.utils";

import type { Document } from "../Types/Document";
import type { Dispatch, SetStateAction } from "react";

const mockApiFetch =
  vi.fn<(url: string, options?: RequestInit) => Promise<Response>>();

vi.mock("../ApiClient", () => ({
  apiFetch: (url: string, options?: RequestInit) => mockApiFetch(url, options),
}));

describe("FilesTableBulkDeleteModal", () => {
  const selectedFiles = [
    makeDocument({ id: 1, name: "report.pdf" }),
    makeDocument({ id: 2, name: "notes.pdf" }),
  ];
  const onClose = vi.fn<() => void>();
  const clearSelectedFiles = vi.fn<() => void>();
  const setFiles = vi.fn<Dispatch<SetStateAction<Document[]>>>();

  beforeEach(() => {
    mockApiFetch.mockReset();
    onClose.mockReset();
    clearSelectedFiles.mockReset();
    setFiles.mockReset();
  });

  it("deletes selected files and closes the modal on success", async () => {
    mockApiFetch.mockResolvedValue({
      ok: true,
    } as Response);

    render(
      <FilesTableBulkDeleteModal
        selectedFiles={selectedFiles}
        clearSelectedFiles={clearSelectedFiles}
        onClose={onClose}
        setFiles={setFiles}
      />,
    );

    expect(
      screen.getByText("Are you sure you want to delete 2 files?"),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith("/api/documents/bulk-delete", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ documentIds: [1, 2] }),
      });
    });

    expect(setFiles).toHaveBeenCalledOnce();
    const updateFiles = setFiles.mock.calls[0][0] as (
      files: Document[],
    ) => Document[];
    expect(
      updateFiles([
        selectedFiles[0],
        selectedFiles[1],
        makeDocument({ id: 3, name: "keep.pdf" }),
      ]),
    ).toEqual([makeDocument({ id: 3, name: "keep.pdf" })]);
    expect(clearSelectedFiles).toHaveBeenCalledOnce();
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("shows an error when delete fails", async () => {
    mockApiFetch.mockResolvedValue({
      ok: false,
      status: 500,
    } as Response);

    render(
      <FilesTableBulkDeleteModal
        selectedFiles={selectedFiles}
        clearSelectedFiles={clearSelectedFiles}
        onClose={onClose}
        setFiles={setFiles}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Delete" }));

    expect(
      await screen.findByText("Failed to delete the files. Please try again."),
    ).toBeInTheDocument();
    expect(setFiles).not.toHaveBeenCalled();
    expect(clearSelectedFiles).not.toHaveBeenCalled();
    expect(onClose).not.toHaveBeenCalled();
  });
});
