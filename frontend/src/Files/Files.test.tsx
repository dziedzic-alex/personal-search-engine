import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Files from "./Files";
import { isFileAllowed } from "./Files.utils";

function makeFile(name: string, type: string): File {
  return new File(["content"], name, { type });
}

describe("isFileAllowed", () => {
  it("allows PDFs by MIME type", () => {
    expect(isFileAllowed(makeFile("doc", "application/pdf"))).toBe(true);
  });

  it("allows images by MIME type", () => {
    expect(isFileAllowed(makeFile("photo", "image/jpeg"))).toBe(true);
  });

  it("allows files by extension when MIME type is empty", () => {
    expect(isFileAllowed(makeFile("scan.heic", ""))).toBe(true);
  });

  it("allows files by extension when MIME type is generic", () => {
    expect(
      isFileAllowed(makeFile("photo.jpg", "application/octet-stream")),
    ).toBe(true);
  });

  it("rejects unsupported file types", () => {
    expect(isFileAllowed(makeFile("notes.txt", "text/plain"))).toBe(false);
  });
});

describe("Files", () => {
  it("shows an error for unsupported files", () => {
    render(<Files />);

    const input = screen.getByLabelText("Upload files");
    const file = new File(["hello"], "notes.txt", { type: "text/plain" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(
      screen.getByText(/files are supported currently/i),
    ).toBeInTheDocument();
  });
});
