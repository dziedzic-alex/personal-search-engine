import ErrorState from "../Ui/ErrorState/ErrorState";
import LoadingPage from "../Ui/LoadingPage/LoadingPage";

import FileCard from "./FileCard";

import type { Document } from "../Types/Document";

import "./FilesGrid.css";
import EmptyState from "../Ui/EmptyState/EmptyState";
import { useNavigate } from "react-router-dom";

interface Props {
  files: Document[];
  isLoading: boolean;
  shouldShowEmptyState: boolean;
  error: string | null;
  retrySearch: () => void;
}

function FilesGrid(props: Props) {
  const { files, isLoading, shouldShowEmptyState, error, retrySearch } = props;

  const navigate = useNavigate();

  if (isLoading) {
    return <LoadingPage />;
  }

  if (error) {
    return (
      <ErrorState title="Error" description={error} onRetry={retrySearch} />
    );
  }

  if (shouldShowEmptyState) {
    return (
      <EmptyState
        title="No processed files"
        description="Upload a file or wait for a file to be processed."
        action={{
          label: "Upload a file",
          onClick: () => {
            void navigate("/files");
          },
        }}
      />
    );
  }

  return (
    <div className="files-grid">
      {files.map((file) => {
        return (
          <FileCard
            key={file.id}
            filename={file.name}
            contentCategory={file.contentCategory}
            thumbnailUrl={file.thumbnailUrl}
            contentUrl={file.contentUrl}
          />
        );
      })}
    </div>
  );
}

export default FilesGrid;
