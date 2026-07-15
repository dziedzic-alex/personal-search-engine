import {
  useState,
  useMemo,
  useEffect,
  type Dispatch,
  type SetStateAction,
} from "react";

import Card from "../Ui/Card/Card";
import Stack from "../Ui/Layout/Stack";
import Header from "../Ui/Typography/Header";

import FilesTable from "./FilesTable";
import SelectedFilesActions from "./SelectedFilesActions";
import TableFilters from "./TableFilters";
import UploadButton from "./UploadButton";
import useGetFiles from "./useGetFiles";

import type { ContentCategory } from "../Types/ContentCategory";
import type { Document } from "../Types/Document";
import type {
  DateFilterOption,
  FilterConfig,
  SortColumnDirection,
} from "../Types/DocumentsListRequest";
import type { DocumentStatus } from "../Types/DocumentStatus";

import "./MyFilesCard.css";

interface Props {
  currentlyExecutedSearchQuery: string | null;
  clearSearch: () => void;
}

function MyFilesCard(props: Props) {
  const { currentlyExecutedSearchQuery, clearSearch } = props;

  const [selectedFiles, setSelectedFiles] = useState<Document[]>([]);
  const [selectedAnchorIndex, setSelectedAnchorIndex] = useState<number | null>(
    null,
  );

  const [typeFilterValue, setTypeFilterValue] =
    useState<ContentCategory | null>(null);
  const [statusFilterValue, setStatusFilterValue] =
    useState<DocumentStatus | null>(null);
  const [dateUploadedFilterValue, setDateUploadedFilterValue] =
    useState<DateFilterOption | null>(null);
  const [dateCreatedFilterValue, setDateCreatedFilterValue] =
    useState<DateFilterOption | null>(null);

  const filterConfig: FilterConfig = useMemo(() => {
    return {
      type: typeFilterValue,
      status: statusFilterValue,
      dateUploaded: dateUploadedFilterValue,
      dateCreated: dateCreatedFilterValue,
    };
  }, [
    typeFilterValue,
    statusFilterValue,
    dateUploadedFilterValue,
    dateCreatedFilterValue,
  ]);

  const [sortColumnDirection, setSortColumnDirection] =
    useState<SortColumnDirection>({
      column: "uploadedTime",
      direction: "desc",
    });

  const {
    files,
    setFiles,
    isLoading,
    error,
    isFetchingMore,
    errorFetchingMore,
    fetchMoreFiles,
    refetchInitialFiles,
  } = useGetFiles({
    filterConfig: filterConfig,
    query: currentlyExecutedSearchQuery,
    sortColumnDirection: sortColumnDirection,
  });

  const clearFilters = () => {
    setTypeFilterValue(null);
    setStatusFilterValue(null);
    setDateUploadedFilterValue(null);
    setDateCreatedFilterValue(null);
  };

  const onClearSelectedFiles = () => {
    clearSelectedFiles(setSelectedFiles, setSelectedAnchorIndex);
  };

  useEffect(() => {
    clearSelectedFiles(setSelectedFiles, setSelectedAnchorIndex);
  }, [sortColumnDirection, currentlyExecutedSearchQuery]);

  return (
    <Card className="my-files-card">
      <Stack spacing="md" fullWidth>
        <Stack direction="horizontal" spacing="md" align="center">
          <Header level={1}>My files</Header>
          <UploadButton setFiles={setFiles} />
        </Stack>
        {selectedFiles.length > 0 ? (
          <SelectedFilesActions
            selectedFiles={selectedFiles}
            onClearSelectedFiles={onClearSelectedFiles}
          />
        ) : (
          <TableFilters
            typeFilterValue={typeFilterValue}
            statusFilterValue={statusFilterValue}
            dateUploadedFilterValue={dateUploadedFilterValue}
            dateCreatedFilterValue={dateCreatedFilterValue}
            setTypeFilterValue={setTypeFilterValue}
            setStatusFilterValue={setStatusFilterValue}
            setDateUploadedFilterValue={setDateUploadedFilterValue}
            setDateCreatedFilterValue={setDateCreatedFilterValue}
          />
        )}
        <FilesTable
          files={files}
          setFiles={setFiles}
          setSortColumnDirection={setSortColumnDirection}
          onClearFilters={clearFilters}
          hasMadeSearchQuery={currentlyExecutedSearchQuery !== null}
          hasAppliedFilters={
            filterConfig.type !== null ||
            filterConfig.status !== null ||
            filterConfig.dateUploaded !== null ||
            filterConfig.dateCreated !== null
          }
          clearSearch={clearSearch}
          fetchNextPage={fetchMoreFiles}
          refetchInitialFiles={refetchInitialFiles}
          isFetchingMore={isFetchingMore}
          errorFetchingMore={errorFetchingMore}
          isLoading={isLoading}
          error={error}
          selectedFiles={selectedFiles}
          selectedAnchorIndex={selectedAnchorIndex}
          setSelectedFiles={setSelectedFiles}
          setSelectedAnchorIndex={setSelectedAnchorIndex}
        />
      </Stack>
    </Card>
  );
}

function clearSelectedFiles(
  setSelectedFiles: Dispatch<SetStateAction<Document[]>>,
  setSelectedAnchorIndex: Dispatch<SetStateAction<number | null>>,
) {
  setSelectedFiles([]);
  setSelectedAnchorIndex(null);
}

export default MyFilesCard;
