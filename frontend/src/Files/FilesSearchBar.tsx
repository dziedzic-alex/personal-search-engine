import { CornerDownLeft } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import SearchBar from "../Ui/SearchBar/SearchBar";
import Body from "../Ui/Typography/Body";
import getContentCategoryIcon from "../Utils/FileIcon";

import useFilesTypeahead from "./useFilesTypeahead";

import "./FilesSearchBar.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
  currentlyExecutedSearch: string | null;
}

function FilesSearchBar(props: Props) {
  const { value, onChange, onSearch, placeholder, currentlyExecutedSearch } =
    props;

  const [debouncedQuery, setDebouncedQuery] = useState<string>(value);
  const [isFocused, setIsFocused] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  const { files, error, hasCompletedFirstFetch } =
    useFilesTypeahead(debouncedQuery);

  const shouldShowPanel = isFocused && value.length > 0;

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(value);
    }, 250);

    return () => {
      clearTimeout(timer);
    };
  }, [value]);

  const commitSearch = () => {
    onSearch();
    inputRef.current?.blur();
  };

  let panelContent;
  if (error) {
    panelContent = (
      <div className="files-search-bar-results-message">
        <Body variant="error">{error}</Body>
      </div>
    );
  } else if (files.length === 0 && hasCompletedFirstFetch) {
    panelContent = (
      <div className="files-search-bar-results-message">
        <Body variant="muted">No files found</Body>
      </div>
    );
  } else {
    const allResultsClassNames = [
      "files-search-bar-all-results-item",
      currentlyExecutedSearch === value
        ? "files-search-bar-all-results-disabled"
        : "",
    ]
      .filter(Boolean)
      .join(" ");

    panelContent = (
      <div>
        {files.map((file) => {
          const icon = getContentCategoryIcon(file.contentCategory);
          return (
            <div
              key={file.id}
              className="files-search-bar-result"
              onMouseDown={(e: React.MouseEvent<HTMLDivElement>) => {
                e.preventDefault();
              }}
              onClick={() => {
                window.open(file.previewUrl, "_blank");
              }}
            >
              {icon}
              {file.name}
            </div>
          );
        })}
        <div
          className={allResultsClassNames}
          onClick={commitSearch}
          onMouseDown={(e: React.MouseEvent<HTMLDivElement>) => {
            e.preventDefault();
          }}
        >
          All Results <CornerDownLeft size={16} />
        </div>
      </div>
    );
  }

  return (
    <div className="files-search-bar-container">
      <SearchBar
        value={value}
        onChange={onChange}
        onSearch={commitSearch}
        placeholder={placeholder}
        onFocus={() => {
          setIsFocused(true);
        }}
        onBlur={() => {
          setIsFocused(false);
        }}
        inputRef={inputRef}
      />
      {shouldShowPanel && (
        <div className="files-search-bar-results">{panelContent}</div>
      )}
    </div>
  );
}

export default FilesSearchBar;
