import { describe, expect, it } from "vitest";

import { isFileAllowed } from "./uploadButton.utils";

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
