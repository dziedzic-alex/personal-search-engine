import {
  ChevronDown,
  ChevronUp,
  CircleCheck,
  CircleX,
  File,
  X,
} from "lucide-react";
import { useState } from "react";

import IconButton from "../../Ui/Buttons/IconButton";
import Card from "../../Ui/Card/Card";
import Stack from "../../Ui/Layout/Stack";
import Spinner from "../../Ui/Spinner/Spinner";
import Body from "../../Ui/Typography/Body";
import Header from "../../Ui/Typography/Header";
import getContentCategoryIcon from "../../Utils/FileIcon";

import "./UploadingFilesPanel.css";
import { ALLOWED_IMAGE_FILE_EXTENSIONS } from "./AllowedFilesConsts";

import type { ContentCategory } from "../../Types/ContentCategory";

export interface UploadingFile {
  file: File;
  uniqueId: string;
  isUploading: boolean;
  error: string | null;
}

interface Props {
  uploadingFiles: UploadingFile[];
  clearUploadingFiles: () => void;
}

function UploadingFilesPanel(props: Props) {
  const { uploadingFiles, clearUploadingFiles } = props;

  const [isExpanded, setIsExpanded] = useState(true);

  const headerText = getHeaderText(uploadingFiles);

  return (
    <Card className="uploading-files-panel">
      <div className="uploading-files-panel-header">
        <Header level={3}>{headerText}</Header>
        <Stack direction="horizontal" align="center" spacing="xs">
          <IconButton
            onClick={() => {
              setIsExpanded(!isExpanded);
            }}
            ariaLabel="Collapse or expand upload panel"
            size="large"
          >
            {isExpanded ? <ChevronDown /> : <ChevronUp />}
          </IconButton>
          <IconButton
            onClick={clearUploadingFiles}
            ariaLabel="Clear upload panel"
            size="large"
          >
            <X />
          </IconButton>
        </Stack>
      </div>
      {isExpanded && (
        <div className="uploading-files-list">
          {uploadingFiles.map((uploadingFile) => (
            <Stack
              key={uploadingFile.uniqueId}
              className="uploading-file-item"
              direction="horizontal"
              align="center"
            >
              <div className="uploading-file-item-icon-container">
                {getFileIconFromTypeOrName(
                  uploadingFile.file.type,
                  uploadingFile.file.name,
                )}
              </div>
              <div className="uploading-file-item-name-container">
                <Body truncate tooltip={uploadingFile.file.name}>
                  {uploadingFile.file.name}
                </Body>
                {uploadingFile.error && (
                  <Body variant="error" truncate tooltip={uploadingFile.error}>
                    {uploadingFile.error}
                  </Body>
                )}
              </div>
              <div className="uploading-file-item-icon-container">
                {getStatusIcon(uploadingFile.isUploading, uploadingFile.error)}
              </div>
            </Stack>
          ))}
        </div>
      )}
    </Card>
  );
}

function getHeaderText(uploadingFiles: UploadingFile[]): string {
  let numFilesCurrentlyUploading = 0;

  uploadingFiles.forEach((uploadingFile) => {
    if (uploadingFile.isUploading) {
      numFilesCurrentlyUploading++;
    }
  });

  if (numFilesCurrentlyUploading > 0) {
    return numFilesCurrentlyUploading === 1
      ? "Uploading 1 file"
      : `Uploading ${String(numFilesCurrentlyUploading)} files`;
  }

  const numUploadsComplete = uploadingFiles.length;

  return numUploadsComplete === 1
    ? "1 upload complete"
    : `${String(numUploadsComplete)} uploads complete`;
}

function getFileIconFromTypeOrName(
  type: string,
  name: string,
): React.ReactNode {
  let contentCategory: ContentCategory | null = null;

  const ext = name.split(".").pop()?.toLowerCase();

  if (
    type.startsWith("image/") ||
    ALLOWED_IMAGE_FILE_EXTENSIONS.includes(ext ?? "")
  ) {
    contentCategory = "image";
  } else if (type === "application/pdf" || ext === "pdf") {
    contentCategory = "pdf";
  }

  if (!contentCategory) {
    return <File />;
  }

  return getContentCategoryIcon(contentCategory);
}

function getStatusIcon(
  isUploading: boolean,
  error: string | null,
): React.ReactNode {
  if (isUploading) {
    return <Spinner size="medium" />;
  }

  if (error) {
    return <CircleX color="red" />;
  }

  return <CircleCheck color="green" />;
}

export default UploadingFilesPanel;
