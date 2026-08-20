import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { makeDocument } from "../filesTest.utils";

import UploadButton from "./UploadButton";

import type { Document } from "../../Types/Document";
import type { Dispatch, SetStateAction } from "react";

const mockApiFetch =
  vi.fn<(url: string, options?: RequestInit) => Promise<Response>>();

vi.mock("../../ApiClient", () => ({
  apiFetch: (url: string, options?: RequestInit) => mockApiFetch(url, options),
}));

function renderUploadButton(
  setFiles: Dispatch<SetStateAction<Document[]>> = vi.fn(),
) {
  return render(<UploadButton setFiles={setFiles} />);
}

async function uploadFile(file: File) {
  const input = screen.getByLabelText("Upload files");
  await userEvent.upload(input, file);
}

describe("UploadButton", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("posts to /api/documents/v2 when the v2 flag is enabled", async () => {
    vi.stubEnv("VITE_IS_DOCUMENT_PROCESSING_V2_ENABLED", "true");
    const document = makeDocument({ id: "1", name: "photo.jpg" });
    mockApiFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(document),
    } as Response);

    const setFiles = vi.fn<Dispatch<SetStateAction<Document[]>>>();
    renderUploadButton(setFiles);

    await uploadFile(
      new File(["content"], "photo.jpg", { type: "image/jpeg" }),
    );

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith(
        "/api/documents/v2",
        expect.objectContaining({ method: "POST" }),
      );
    });

    await waitFor(() => {
      expect(setFiles).toHaveBeenCalled();
    });
  });

  it("posts to /api/documents/ when the v2 flag is disabled", async () => {
    vi.stubEnv("VITE_IS_DOCUMENT_PROCESSING_V2_ENABLED", "false");
    mockApiFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(makeDocument()),
    } as Response);

    renderUploadButton();

    await uploadFile(
      new File(["content"], "report.pdf", { type: "application/pdf" }),
    );

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith(
        "/api/documents/",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("shows an image-too-large message on 413", async () => {
    vi.stubEnv("VITE_IS_DOCUMENT_PROCESSING_V2_ENABLED", "true");
    mockApiFetch.mockResolvedValue({
      ok: false,
      status: 413,
    } as Response);

    renderUploadButton();

    await uploadFile(new File(["content"], "huge.jpg", { type: "image/jpeg" }));

    expect(
      await screen.findByText(
        "Image is too large. The maximum allowed size is 5MB",
      ),
    ).toBeInTheDocument();
  });
});
