import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import FilesTableRenameModal from "./FilesTableRenameModal";
import { makeDocument } from "./filesTest.utils";

import type { Document } from "../Types/Document";
import type { Dispatch, SetStateAction } from "react";

const mockApiFetch =
  vi.fn<(url: string, options?: RequestInit) => Promise<Response>>();

vi.mock("../ApiClient", () => ({
  apiFetch: (url: string, options?: RequestInit) => mockApiFetch(url, options),
}));

describe("FilesTableRenameModal", () => {
  const file = makeDocument({ id: 42, name: "report.pdf" });
  const onClose = vi.fn<() => void>();
  const setFiles = vi.fn<Dispatch<SetStateAction<Document[]>>>();

  beforeEach(() => {
    mockApiFetch.mockReset();
    onClose.mockReset();
    setFiles.mockReset();
  });

  it("renames the file and closes the modal on success", async () => {
    const updatedFile = makeDocument({ id: 42, name: "annual report.pdf" });
    mockApiFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(updatedFile),
    } as Response);

    render(
      <FilesTableRenameModal
        file={file}
        onClose={onClose}
        setFiles={setFiles}
      />,
    );

    await userEvent.clear(screen.getByPlaceholderText("Enter new name"));
    await userEvent.type(
      screen.getByPlaceholderText("Enter new name"),
      "annual report.pdf",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith("/api/documents/42", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: "annual report.pdf" }),
      });
    });

    expect(setFiles).toHaveBeenCalledOnce();
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("shows an error when rename fails", async () => {
    mockApiFetch.mockResolvedValue({
      ok: false,
      status: 500,
    } as Response);

    render(
      <FilesTableRenameModal
        file={file}
        onClose={onClose}
        setFiles={setFiles}
      />,
    );

    await userEvent.clear(screen.getByPlaceholderText("Enter new name"));
    await userEvent.type(
      screen.getByPlaceholderText("Enter new name"),
      "new.pdf",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(
      await screen.findByText("Failed to rename the file. Please try again."),
    ).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(setFiles).not.toHaveBeenCalled();
  });

  it("shows a duplicate name error when rename returns 409", async () => {
    mockApiFetch.mockResolvedValue({
      ok: false,
      status: 409,
    } as Response);

    render(
      <FilesTableRenameModal
        file={file}
        onClose={onClose}
        setFiles={setFiles}
      />,
    );

    await userEvent.clear(screen.getByPlaceholderText("Enter new name"));
    await userEvent.type(
      screen.getByPlaceholderText("Enter new name"),
      "existing.pdf",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(
      await screen.findByText(
        "Document with name 'existing.pdf' already exists",
      ),
    ).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(setFiles).not.toHaveBeenCalled();
  });
});
