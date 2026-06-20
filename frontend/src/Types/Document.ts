import type { ContentCategory } from "./ContentCategory";
import type { DocumentStatus } from "./DocumentStatus";

export const MAX_NUM_PROCESSING_ATTEMPTS = 3;

export interface Document {
  id: number;
  name: string;
  contentCategory: ContentCategory;
  status: DocumentStatus;
  numAttempts: number;
  contentUrl: string;
  thumbnailUrl: string;
  size: number;
  sourceCreatedTime: string | null;
  uploadedTime: string;
}
