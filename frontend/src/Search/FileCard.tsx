import { Download, EllipsisVertical, Eye } from "lucide-react";

import ActionMenu, {
  type ActionMenuTriggerProps,
} from "../Ui/ActionMenu/ActionMenu";
import IconButton from "../Ui/Buttons/IconButton";
import Card from "../Ui/Card/Card";
import Stack from "../Ui/Layout/Stack";
import getContentCategoryIcon from "../Utils/FileIcon";

import type { ContentCategory } from "../Types/ContentCategory";

import "./FileCard.css";

interface Props {
  filename: string;
  contentCategory: ContentCategory;
  thumbnailUrl: string;
  previewUrl: string;
  downloadUrl: string;
}

function FileCard(props: Props) {
  const { filename, contentCategory, thumbnailUrl, previewUrl, downloadUrl } =
    props;

  const thumbnailClassNames = [
    "file-card-thumbnail",
    contentCategory === "pdf" ? "file-card-thumbnail-pdf" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <Card className="file-card">
      <a
        href={previewUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="file-card-link"
        aria-label={`Open ${filename}`}
      />
      <Stack className="file-card-content">
        <div className="file-card-header">
          <div className="file-card-icon">
            {getContentCategoryIcon(contentCategory)}
          </div>
          <div className="file-card-name">{filename}</div>
          <div className="file-card-actions">
            <ActionMenu
              renderTrigger={(triggerProps: ActionMenuTriggerProps) => (
                <IconButton ariaLabel="Actions" size="medium" {...triggerProps}>
                  <EllipsisVertical />
                </IconButton>
              )}
              options={[
                {
                  id: "view",
                  label: "View",
                  icon: Eye,
                  onClick: () => {
                    window.open(previewUrl, "_blank");
                  },
                },
                {
                  id: "download",
                  label: "Download",
                  icon: Download,
                  onClick: () => {
                    window.location.assign(downloadUrl);
                  },
                },
              ]}
            />
          </div>
        </div>
        <img src={thumbnailUrl} alt="" className={thumbnailClassNames} />
      </Stack>
    </Card>
  );
}

export default FileCard;
