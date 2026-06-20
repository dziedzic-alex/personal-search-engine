import { useMemo, useState, type Dispatch, type SetStateAction } from "react";

import Card from "../Ui/Card";
import Stack from "../Ui/Layout/Stack";
import Header from "../Ui/Typography/Header";

import FilesTable from "./FilesTable";
import TableFilters from "./TableFilters";
import UploadButton from "./UploadButton";

import type { DateFilterOption } from "./dateFilter.utils";
import type { FilterConfig } from "./filesTable.utils";
import type { ContentCategory } from "../Types/ContentCategory";
import type { Document } from "../Types/Document";
import type { DocumentStatus } from "../Types/DocumentStatus";

interface Props {
  files: Document[];
  setFiles: Dispatch<SetStateAction<Document[]>>;
}

function MyFilesCard(props: Props) {
  const { files, setFiles } = props;

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

  return (
    <Card>
      <Stack spacing="md">
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
        />
      </Stack>
    </Card>
  );
}

export default MyFilesCard;
