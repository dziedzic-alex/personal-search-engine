import { passesDateFilter, type DateFilterOption } from "./dateFilter.utils";

import type { ContentCategory } from "../Types/ContentCategory";
import type { Document } from "../Types/Document";
import type { DocumentStatus } from "../Types/DocumentStatus";

export interface FilterConfig {
  type: ContentCategory | null;
  status: DocumentStatus | null;
  dateUploaded: DateFilterOption | null;
  dateCreated: DateFilterOption | null;
}

export type SortDirection = "asc" | "desc";
export type SortColumn = "name" | "uploadedTime" | "sourceCreatedTime" | "size";

export interface SortColumnDirection {
  column: SortColumn;
  direction: SortDirection;
}

export function filterFiles(
  files: Document[],
  filterConfig: FilterConfig,
): Document[] {
  return files.filter((file) => {
    if (
      filterConfig.type !== null &&
      filterConfig.type !== file.contentCategory
    ) {
      return false;
    }

    if (filterConfig.status !== null && filterConfig.status !== file.status) {
      return false;
    }

    if (
      filterConfig.dateUploaded !== null &&
      !passesDateFilter(filterConfig.dateUploaded, file.uploadedTime)
    ) {
      return false;
    }

    if (
      filterConfig.dateCreated !== null &&
      !passesDateFilter(filterConfig.dateCreated, file.sourceCreatedTime)
    ) {
      return false;
    }

    return true;
  });
}

export function sortFiles(
  files: Document[],
  sortColumnDirection: SortColumnDirection | null,
): Document[] {
  if (sortColumnDirection === null) {
    return files;
  }

  const { column, direction } = sortColumnDirection;

  return [...files].sort((a, b) => {
    switch (column) {
      case "name":
        return direction === "asc"
          ? a.name.localeCompare(b.name)
          : b.name.localeCompare(a.name);
      case "uploadedTime": {
        const uploadedA = new Date(a.uploadedTime);
        const uploadedB = new Date(b.uploadedTime);

        return direction === "asc"
          ? uploadedA.getTime() - uploadedB.getTime()
          : uploadedB.getTime() - uploadedA.getTime();
      }
      case "sourceCreatedTime": {
        const createdA = a.sourceCreatedTime
          ? new Date(a.sourceCreatedTime)
          : null;
        const createdB = b.sourceCreatedTime
          ? new Date(b.sourceCreatedTime)
          : null;

        if (createdA == null && createdB == null) {
          return 0;
        } else if (createdA === null) {
          return 1;
        } else if (createdB === null) {
          return -1;
        }

        return direction === "asc"
          ? createdA.getTime() - createdB.getTime()
          : createdB.getTime() - createdA.getTime();
      }
      case "size":
        return direction === "asc" ? a.size - b.size : b.size - a.size;
    }
  });
}
