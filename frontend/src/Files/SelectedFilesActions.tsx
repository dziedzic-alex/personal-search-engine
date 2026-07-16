import { Download, Trash2, X } from "lucide-react";

import IconButton from "../Ui/Buttons/IconButton";
import Stack from "../Ui/Layout/Stack";
import Body from "../Ui/Typography/Body";

import type { Document } from "../Types/Document";

import "./SelectedFilesActions.css";

interface Props {
  selectedFiles: Document[];
  onClearSelectedFiles: () => void;
  handleDelete: () => Promise<void>;
}

function SelectedFilesActions(props: Props) {
  const { selectedFiles, onClearSelectedFiles, handleDelete } = props;

  const selectedCountText =
    selectedFiles.length === 1
      ? "1 file selected"
      : `${String(selectedFiles.length)} files selected`;

  const handleDownload = () => {
    if (selectedFiles.length === 1) {
      window.location.assign(selectedFiles[0].downloadUrl);
      return;
    }
  };

  return (
    <div className="selected-files-actions-container">
      <Stack direction="horizontal" spacing="md" align="center">
        <IconButton
          ariaLabel="Clear selected files"
          onClick={onClearSelectedFiles}
        >
          <X />
        </IconButton>
        <Body>{selectedCountText}</Body>
        <div>
          <IconButton
            ariaLabel="Download selected files"
            onClick={handleDownload}
          >
            <Download />
          </IconButton>
          <IconButton
            ariaLabel="Delete selected files"
            onClick={() => void handleDelete()}
          >
            <Trash2 />
          </IconButton>
        </div>
      </Stack>
    </div>
  );
}

export default SelectedFilesActions;
