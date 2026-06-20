import { describe, expect, it } from "vitest";

import { filterFiles, sortFiles } from "./filesTable.utils";
import { makeDocument } from "./filesTest.utils";

describe("filterFiles", () => {
  const files = [
    makeDocument({
      id: 1,
      name: "alpha.pdf",
      contentCategory: "pdf",
      status: "processed",
      uploadedTime: "2025-06-10T00:00:00",
    }),
    makeDocument({
      id: 2,
      name: "beta.jpg",
      contentCategory: "image",
      status: "failed",
      uploadedTime: "2025-06-01T00:00:00",
      sourceCreatedTime: null,
    }),
  ];

  it("returns all files when no filters are set", () => {
    expect(
      filterFiles(files, {
        type: null,
        status: null,
        dateUploaded: null,
        dateCreated: null,
      }),
    ).toEqual(files);
  });

  it("filters by type and status", () => {
    expect(
      filterFiles(files, {
        type: "image",
        status: "failed",
        dateUploaded: null,
        dateCreated: null,
      }),
    ).toEqual([files[1]]);
  });
});

describe("sortFiles", () => {
  const files = [
    makeDocument({ id: 1, name: "charlie.pdf", size: 300 }),
    makeDocument({ id: 2, name: "alpha.pdf", size: 100 }),
    makeDocument({ id: 3, name: "bravo.pdf", size: 200 }),
  ];

  it("returns files unchanged when sort is null", () => {
    expect(sortFiles(files, null)).toEqual(files);
  });

  it("sorts by name ascending", () => {
    expect(
      sortFiles(files, { column: "name", direction: "asc" }).map((f) => f.name),
    ).toEqual(["alpha.pdf", "bravo.pdf", "charlie.pdf"]);
  });

  it("sorts by size descending", () => {
    expect(
      sortFiles(files, { column: "size", direction: "desc" }).map(
        (f) => f.size,
      ),
    ).toEqual([300, 200, 100]);
  });
});
