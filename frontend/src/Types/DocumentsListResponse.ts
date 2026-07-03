import type { Document } from "./Document";

export interface DocumentsListResponse {
  documents: Document[];
  nextPage: number | null;
}
