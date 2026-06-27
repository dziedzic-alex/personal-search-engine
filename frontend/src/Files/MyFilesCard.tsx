import { useMemo, useState, type Dispatch, type SetStateAction } from "react";

import Card from "../Ui/Card/Card";
import Stack from "../Ui/Layout/Stack";
import LoadingPage from "../Ui/LoadingPage/LoadingPage";
import Header from "../Ui/Typography/Header";

import FilesTable from "./FilesTable";
import TableFilters from "./TableFilters";
import UploadButton from "./UploadButton";

import type { DateFilterOption } from "./dateFilter.utils";
import type { FilterConfig } from "./filesTable.utils";
import type { ContentCategory } from "../Types/ContentCategory";
import type { Document } from "../Types/Document";
import type { DocumentStatus } from "../Types/DocumentStatus";

import "./MyFilesCard.css";

interface Props {
  files: Document[];
  setFiles: Dispatch<SetStateAction<Document[]>>;
  isLoadingFiles: boolean;
  hasMadeSearchQuery: boolean;
  clearSearch: () => void;
}

function MyFilesCard(props: Props) {
  const { files, setFiles, isLoadingFiles, hasMadeSearchQuery, clearSearch } =
    props;

  const [typeFilterValue, setTypeFilterValue] =
    useState<ContentCategory | null>(null);
  const [statusFilterValue, setStatusFilterValue] =
    useState<DocumentStatus | null>(null);
  const [dateUploadedFilterValue, setDateUploadedFilterValue] =
    useState<DateFilterOption | null>(null);
  const [dateCreatedFilterValue, setDateCreatedFilterValue] =
    useState<DateFilterOption | null>(null);

  const filterConfig: FilterConfig = useMemo(
    () => ({
      type: typeFilterValue,
      status: statusFilterValue,
      dateUploaded: dateUploadedFilterValue,
      dateCreated: dateCreatedFilterValue,
    }),
    [
      typeFilterValue,
      statusFilterValue,
      dateUploadedFilterValue,
      dateCreatedFilterValue,
    ],
  );

  const clearFilters = () => {
    setTypeFilterValue(null);
    setStatusFilterValue(null);
    setDateUploadedFilterValue(null);
    setDateCreatedFilterValue(null);
  };

  return (
    <Card className="my-files-card">
      {isLoadingFiles ? (
        <LoadingPage />
      ) : (
        <Stack spacing="md" fullWidth>
          <Stack direction="horizontal" spacing="md" align="center">
            <Header level={1}>My files</Header>
            <UploadButton setFiles={setFiles} />
          </Stack>
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
          <FilesTable
            files={files}
            setFiles={setFiles}
            filterConfig={filterConfig}
            onClearFilters={clearFilters}
            hasMadeSearchQuery={hasMadeSearchQuery}
            clearSearch={clearSearch}
          />
        </Stack>
      )}
    </Card>
  );
}

export default MyFilesCard;
