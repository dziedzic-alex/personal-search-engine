import type { ContentCategory } from "./ContentCategory";
import type { DocumentStatus } from "./DocumentStatus";

export interface FilterConfig {
  type: ContentCategory | null;
  status: DocumentStatus | null;
  dateUploaded: DateFilterOption | null;
  dateCreated: DateFilterOption | null;
}

export type DateFilterOption =
  | "today"
  | "last7Days"
  | "last30Days"
  | "thisYear"
  | "lastYear";

export interface SortColumnDirection {
  column: SortColumn;
  direction: SortDirection;
}

export type SortDirection = "asc" | "desc";
export type SortColumn = "name" | "uploadedTime" | "sourceCreatedTime" | "size";

export interface DocumentsListRequest {
  filterConfig?: FilterConfig | null;
  query?: string | null;
  sortConfig?: SortColumnDirection | null;
  page?: number;
}
