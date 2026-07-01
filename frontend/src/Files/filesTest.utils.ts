import type { Document } from "../Types/Document";

export function makeDocument(overrides: Partial<Document> = {}): Document {
  return {
    id: 1,
    name: "report.pdf",
    contentCategory: "pdf",
    status: "processed",
    previewUrl: "https://presigned.example/1/report.pdf",
    downloadUrl: "https://presigned.example/1/report.pdf",
    thumbnailUrl: "",
    size: 1024,
    sourceCreatedTime: "2025-01-01T00:00:00",
    uploadedTime: "2025-06-01T00:00:00",
    ...overrides,
  };
}
