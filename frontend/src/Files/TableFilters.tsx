import { Clock, Check, X, Calendar, FileText, Image } from "lucide-react";

import Dropdown from "../Ui/Dropdown/Dropdown";
import Stack from "../Ui/Layout/Stack";

import type { ContentCategory } from "../Types/ContentCategory";
import type { DateFilterOption } from "../Types/DocumentsListRequest";
import type { DocumentStatus } from "../Types/DocumentStatus";
import type { DropdownOption } from "../Ui/Dropdown/DropdownOption";
import type { Dispatch, SetStateAction } from "react";

const TYPE_FILTER_DROPDOWN_OPTIONS: DropdownOption[] = [
  { id: "pdf", label: "PDFs", icon: FileText },
  { id: "image", label: "Images", icon: Image },
];

const STATUS_FILTER_DROPDOWN_OPTIONS: DropdownOption[] = [
  { id: "pending", label: "Pending", icon: Clock },
  { id: "processing", label: "Processing", icon: Clock },
  { id: "processed", label: "Processed", icon: Check },
  { id: "failed", label: "Failed", icon: X, iconColor: "#8b4a42" },
];

const DATE_FILTER_DROPDOWN_OPTIONS: DropdownOption[] = [
  { id: "today", label: "Today", icon: Calendar },
  { id: "last7Days", label: "Last 7 days", icon: Calendar },
  { id: "last30Days", label: "Last 30 days", icon: Calendar },
  { id: "thisYear", label: "This year", icon: Calendar },
  { id: "lastYear", label: "Last year", icon: Calendar },
];

interface Props {
  typeFilterValue: ContentCategory | null;
  statusFilterValue: DocumentStatus | null;
  dateUploadedFilterValue: DateFilterOption | null;
  dateCreatedFilterValue: DateFilterOption | null;
  setTypeFilterValue: Dispatch<SetStateAction<ContentCategory | null>>;
  setStatusFilterValue: Dispatch<SetStateAction<DocumentStatus | null>>;
  setDateUploadedFilterValue: Dispatch<SetStateAction<DateFilterOption | null>>;
  setDateCreatedFilterValue: Dispatch<SetStateAction<DateFilterOption | null>>;
}

function TableFilters(props: Props) {
  const {
    typeFilterValue,
    statusFilterValue,
    dateUploadedFilterValue,
    dateCreatedFilterValue,
    setTypeFilterValue,
    setStatusFilterValue,
    setDateUploadedFilterValue,
    setDateCreatedFilterValue,
  } = props;

  return (
    <Stack direction="horizontal" spacing="sm">
      <Dropdown
        label="Type"
        value={typeFilterValue}
        options={TYPE_FILTER_DROPDOWN_OPTIONS}
        onChange={(id) => {
          if (id === typeFilterValue) {
            setTypeFilterValue(null);
            return;
          }

          setTypeFilterValue(id as ContentCategory);
        }}
      />
      <Dropdown
        label="Status"
        value={statusFilterValue}
        options={STATUS_FILTER_DROPDOWN_OPTIONS}
        onChange={(id) => {
          if (id === statusFilterValue) {
            setStatusFilterValue(null);
            return;
          }

          setStatusFilterValue(id as DocumentStatus);
        }}
      />
      <Dropdown
        label="Date uploaded"
        value={dateUploadedFilterValue}
        options={DATE_FILTER_DROPDOWN_OPTIONS}
        onChange={(id) => {
          if (id === dateUploadedFilterValue) {
            setDateUploadedFilterValue(null);
            return;
          }

          setDateUploadedFilterValue(id as DateFilterOption);
        }}
      />
      <Dropdown
        label="Date created"
        value={dateCreatedFilterValue}
        options={DATE_FILTER_DROPDOWN_OPTIONS}
        onChange={(id) => {
          if (id === dateCreatedFilterValue) {
            setDateCreatedFilterValue(null);
            return;
          }

          setDateCreatedFilterValue(id as DateFilterOption);
        }}
      />
    </Stack>
  );
}

export default TableFilters;
