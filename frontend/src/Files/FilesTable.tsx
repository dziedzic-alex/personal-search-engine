import { ArrowDown, ArrowUp, FileText, Image } from "lucide-react";
import { useMemo, useState } from "react";

import Badge from "../Ui/Badge";
import EmptyState from "../Ui/EmptyState/EmptyState";
import Stack from "../Ui/Layout/Stack";
import Table from "../Ui/Table/Table";
import TableBody from "../Ui/Table/TableBody";
import TableCell from "../Ui/Table/TableCell";
import TableHeader from "../Ui/Table/TableHeader";
import TableRow from "../Ui/Table/TableRow";
import { formatBytes } from "../Utils/Bytes";
import { formatDate } from "../Utils/Date";

import {
  filterFiles,
  sortFiles,
  type FilterConfig,
  type SortColumn,
  type SortColumnDirection,
  type SortDirection,
} from "./filesTable.utils";
import FilesTableRowActionMenu from "./FilesTableRowActionMenu";

import type { ContentCategory } from "../Types/ContentCategory";
import type { Document } from "../Types/Document";
import type { DocumentStatus } from "../Types/DocumentStatus";
import type { Dispatch, SetStateAction } from "react";

interface Props {
  files: Document[];
  setFiles: Dispatch<SetStateAction<Document[]>>;
  filterConfig: FilterConfig;
}

function FilesTable(props: Props) {
  const { files, setFiles, filterConfig } = props;

  const [sortColumnDirection, setSortColumnDirection] =
    useState<SortColumnDirection | null>(null);

  const updateSortColumnDirection = (newSortColumn: SortColumn) => {
    let newDirection: SortDirection = "asc";
    if (sortColumnDirection?.column === newSortColumn) {
      newDirection = sortColumnDirection.direction === "asc" ? "desc" : "asc";
    }
    setSortColumnDirection({ column: newSortColumn, direction: newDirection });
  };

  const tableFiles = useMemo(
    () => sortFiles(filterFiles(files, filterConfig), sortColumnDirection),
    [files, filterConfig, sortColumnDirection],
  );

  if (files.length === 0) {
    return (
      <EmptyState
        title="No files yet"
        description="Upload a file to get started."
      />
    );
  }

  if (tableFiles.length === 0) {
    return (
      <EmptyState
        title="No matching files"
        description="Try adjusting your filters."
      />
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSortColumnDirection("name");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              Name
              {getSortDirectionIcon("name", sortColumnDirection)}
            </Stack>
          </TableCell>
          <TableCell as="th">Status</TableCell>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSortColumnDirection("uploadedTime");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              Date uploaded
              {getSortDirectionIcon("uploadedTime", sortColumnDirection)}
            </Stack>
          </TableCell>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSortColumnDirection("sourceCreatedTime");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              Date created
              {getSortDirectionIcon("sourceCreatedTime", sortColumnDirection)}
            </Stack>
          </TableCell>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSortColumnDirection("size");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              File size
              {getSortDirectionIcon("size", sortColumnDirection)}
            </Stack>
          </TableCell>
          <TableCell as="th">
            <span></span>
          </TableCell>
        </TableRow>
      </TableHeader>
      <TableBody>
        {tableFiles.map((file) => (
          <TableRow key={file.id}>
            <TableCell>
              <Stack direction="horizontal" spacing="sm">
                {getContentCategoryIcon(file.contentCategory)}
                {file.name}
              </Stack>
            </TableCell>
            <TableCell>{getDocumentStatusBadge(file.status)}</TableCell>
            <TableCell>{formatDate(file.uploadedTime)}</TableCell>
            <TableCell>
              {file.sourceCreatedTime
                ? formatDate(file.sourceCreatedTime)
                : "N/A"}
            </TableCell>
            <TableCell>{formatBytes(file.size)}</TableCell>
            <TableCell>
              <FilesTableRowActionMenu file={file} setFiles={setFiles} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function getContentCategoryIcon(
  contentCategory: ContentCategory,
): React.ReactNode {
  switch (contentCategory) {
    case "pdf":
      return <FileText />;
    case "image":
      return <Image />;
  }
}

function getDocumentStatusBadge(status: DocumentStatus): React.ReactNode {
  switch (status) {
    case "pending":
      return <Badge level="neutral">Pending</Badge>;
    case "processing":
      return <Badge level="info">Processing</Badge>;
    case "processed":
      return <Badge level="success">Processed</Badge>;
    case "failed":
      return <Badge level="danger">Failed</Badge>;
  }
}

function getSortDirectionIcon(
  column: SortColumn,
  currentSortColumnDirection: SortColumnDirection | null,
): React.ReactNode {
  const iconSize = 16;
  const isActive = currentSortColumnDirection?.column === column;

  return (
    <span className="sort-icon-slot" aria-hidden>
      {isActive &&
        (currentSortColumnDirection.direction === "asc" ? (
          <ArrowUp size={iconSize} />
        ) : (
          <ArrowDown size={iconSize} />
        ))}
    </span>
  );
}

export default FilesTable;
