import { ArrowDown, ArrowUp } from "lucide-react";
import { useEffect, useState } from "react";

import Badge from "../Ui/Badge/Badge";
import EmptyState from "../Ui/EmptyState/EmptyState";
import ErrorState from "../Ui/ErrorState/ErrorState";
import Stack from "../Ui/Layout/Stack";
import LoadingPage from "../Ui/LoadingPage/LoadingPage";
import { notify } from "../Ui/Notification/notify";
import Spinner from "../Ui/Spinner/Spinner";
import Table from "../Ui/Table/Table";
import TableBody from "../Ui/Table/TableBody";
import TableCell from "../Ui/Table/TableCell";
import TableHeader from "../Ui/Table/TableHeader";
import TableRow from "../Ui/Table/TableRow";
import { formatBytes } from "../Utils/Bytes";
import { formatDate } from "../Utils/Date";
import getContentCategoryIcon from "../Utils/FileIcon";

import FilesTableRowActionMenu from "./FilesTableRowActionMenu";

import type { Document } from "../Types/Document";
import type {
  SortColumn,
  SortColumnDirection,
  SortDirection,
} from "../Types/DocumentsListRequest";
import type { DocumentStatus } from "../Types/DocumentStatus";
import type { Dispatch, SetStateAction } from "react";

import "./FilesTable.css";

interface Props {
  files: Document[];
  setFiles: Dispatch<SetStateAction<Document[]>>;
  setSortColumnDirection: Dispatch<SetStateAction<SortColumnDirection>>;
  onClearFilters: () => void;
  hasMadeSearchQuery: boolean;
  hasAppliedFilters: boolean;
  clearSearch: () => void;
  fetchNextPage: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
  isFetchingMore: boolean;
  errorFetchingMore: string | null;
  refetchInitialFiles: () => void;
  selectedFiles: Document[];
  selectedAnchorIndex: number | null;
  setSelectedFiles: Dispatch<SetStateAction<Document[]>>;
  setSelectedAnchorIndex: Dispatch<SetStateAction<number | null>>;
  handleDelete: () => Promise<void>;
}

function FilesTable(props: Props) {
  const {
    files,
    setFiles,
    setSortColumnDirection,
    onClearFilters,
    hasMadeSearchQuery,
    hasAppliedFilters,
    clearSearch,
    fetchNextPage,
    isLoading,
    error,
    isFetchingMore,
    errorFetchingMore,
    refetchInitialFiles,
    selectedFiles,
    selectedAnchorIndex,
    setSelectedFiles,
    setSelectedAnchorIndex,
    handleDelete,
  } = props;

  const [sortColumn, setSortColumn] = useState<SortColumn>("uploadedTime");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const updateSort = (newSortColumn: SortColumn) => {
    let newDirection: SortDirection = "asc";
    if (sortColumn === newSortColumn) {
      newDirection = sortDirection === "asc" ? "desc" : "asc";
    }
    setSortColumn(newSortColumn);
    setSortDirection(newDirection);
    setSortColumnDirection({
      column: newSortColumn,
      direction: newDirection,
    });
  };

  const handleScroll = (event: React.UIEvent<HTMLDivElement>) => {
    if (isFetchingMore) {
      return;
    }

    const { scrollTop, scrollHeight, clientHeight } = event.currentTarget;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    if (distanceFromBottom <= 1) {
      void fetchNextPage();
    }
  };

  const handleRowClick = (
    file: Document,
    event: React.MouseEvent<HTMLTableRowElement>,
  ) => {
    const currentFileIndex = files.findIndex((f) => f.id === file.id);
    if (currentFileIndex === -1) {
      return;
    }

    const { metaKey, ctrlKey, shiftKey } = event;

    if (shiftKey && selectedAnchorIndex !== null) {
      const startIndex = Math.min(selectedAnchorIndex, currentFileIndex);
      const endIndex = Math.max(selectedAnchorIndex, currentFileIndex);

      const shiftSelectedFilesIds = new Set<number>();
      const shiftSelectedFiles: Document[] = [];

      for (let i = startIndex; i < endIndex + 1; i++) {
        shiftSelectedFilesIds.add(files[i].id);
        shiftSelectedFiles.push(files[i]);
      }

      const selectedFilesNotInShiftSelectedFiles: Document[] =
        selectedFiles.filter((f) => !shiftSelectedFilesIds.has(f.id));

      setSelectedFiles([
        ...selectedFilesNotInShiftSelectedFiles,
        ...shiftSelectedFiles,
      ]);
    } else if (metaKey || ctrlKey) {
      const isFileSelected = selectedFiles.some((f) => f.id === file.id);

      if (isFileSelected) {
        setSelectedFiles((prevFiles) =>
          prevFiles.filter((f) => f.id !== file.id),
        );
      } else {
        setSelectedFiles((prevFiles) => [...prevFiles, file]);
      }
    } else {
      setSelectedFiles([file]);
    }

    setSelectedAnchorIndex(currentFileIndex);
  };

  const handleDoubleClick = (file: Document) => {
    window.open(file.previewUrl, "_blank");
  };

  useEffect(() => {
    if (errorFetchingMore) {
      notify({
        message: errorFetchingMore,
        variant: "error",
      });
    }
  }, [errorFetchingMore]);

  if (isLoading) {
    return <LoadingPage />;
  }

  if (error) {
    return (
      <ErrorState
        title="Error loading files"
        description={error}
        onRetry={refetchInitialFiles}
        fullHeight
      />
    );
  }

  if (files.length === 0 && !hasMadeSearchQuery && !hasAppliedFilters) {
    return (
      <EmptyState
        title="No files yet"
        description="Upload a file to get started."
        fullHeight
      />
    );
  } else if (files.length === 0 && hasMadeSearchQuery && hasAppliedFilters) {
    return (
      <EmptyState
        title="No matching files"
        description="Try adjusting your search query or filters."
        action={{
          label: "Clear search & filters",
          onClick: () => {
            clearSearch();
            onClearFilters();
          },
        }}
        fullHeight
      />
    );
  } else if (files.length === 0 && hasMadeSearchQuery && !hasAppliedFilters) {
    return (
      <EmptyState
        title="No matching files"
        description="Try adjusting your search query."
        action={{ label: "Clear search", onClick: clearSearch }}
        fullHeight
      />
    );
  } else if (files.length === 0 && !hasMadeSearchQuery && hasAppliedFilters) {
    return (
      <EmptyState
        title="No matching files"
        description="Try adjusting your filters."
        action={{ label: "Clear filters", onClick: onClearFilters }}
        fullHeight
      />
    );
  }

  return (
    <Table onScroll={handleScroll}>
      <TableHeader>
        <TableRow>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSort("name");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              Name
              {getSortDirectionIcon("name", sortColumn, sortDirection)}
            </Stack>
          </TableCell>
          <TableCell as="th">Status</TableCell>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSort("uploadedTime");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              Date uploaded
              {getSortDirectionIcon("uploadedTime", sortColumn, sortDirection)}
            </Stack>
          </TableCell>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSort("sourceCreatedTime");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              Date created
              {getSortDirectionIcon(
                "sourceCreatedTime",
                sortColumn,
                sortDirection,
              )}
            </Stack>
          </TableCell>
          <TableCell
            as="th"
            sortable
            onClick={() => {
              updateSort("size");
            }}
          >
            <Stack direction="horizontal" spacing="xs" align="center">
              File size
              {getSortDirectionIcon("size", sortColumn, sortDirection)}
            </Stack>
          </TableCell>
          <TableCell as="th">
            <span></span>
          </TableCell>
        </TableRow>
      </TableHeader>
      <TableBody>
        {files.map((file) => (
          <TableRow
            key={file.id}
            onClick={(event) => {
              handleRowClick(file, event);
            }}
            onDoubleClick={() => {
              handleDoubleClick(file);
            }}
            isSelected={selectedFiles.some(
              (selectedFile) => selectedFile.id === file.id,
            )}
          >
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
              <FilesTableRowActionMenu
                file={file}
                setFiles={setFiles}
                handleDelete={handleDelete}
              />
            </TableCell>
          </TableRow>
        ))}
        {isFetchingMore && (
          <TableRow>
            <TableCell colSpan={6}>
              <div className="loading-more-files-container">
                <Spinner size="large" />
              </div>
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
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
  currentSortColumn: SortColumn | null,
  currentSortDirection: SortDirection | null,
): React.ReactNode {
  const iconSize = 16;
  const isActive = currentSortColumn === column;

  return (
    <span className="sort-icon-slot" aria-hidden>
      {isActive &&
        (currentSortDirection === "asc" ? (
          <ArrowUp size={iconSize} />
        ) : (
          <ArrowDown size={iconSize} />
        ))}
    </span>
  );
}

export default FilesTable;
