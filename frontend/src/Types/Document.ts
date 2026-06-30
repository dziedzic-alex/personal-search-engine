import type { ContentCategory } from "./ContentCategory";
import type { DocumentStatus } from "./DocumentStatus";

export interface Document {
  id: number;
  name: string;
  contentCategory: ContentCategory;
  status: DocumentStatus;
  previewUrl: string;
  downloadUrl: string;
  thumbnailUrl: string;
  size: number;
  sourceCreatedTime: string | null;
  uploadedTime: string;
}
