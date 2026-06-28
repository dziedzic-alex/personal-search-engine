import { FileText, Image } from "lucide-react";

import type { ContentCategory } from "../Types/ContentCategory";
import type { ReactNode } from "react";

function getContentCategoryIcon(contentCategory: ContentCategory): ReactNode {
  switch (contentCategory) {
    case "pdf":
      return <FileText />;
    case "image":
      return <Image />;
  }
}

export default getContentCategoryIcon;
