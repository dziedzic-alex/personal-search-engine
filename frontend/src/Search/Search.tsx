import { FileText, Image } from "lucide-react";
import { useState } from "react";

import { apiFetch } from "../ApiClient";
import SearchBar from "../Ui/SearchBar/SearchBar";
import SegmentedControl from "../Ui/SegmentedControl/SegmentedControl";
import Header from "../Ui/Typography/Header";

import FilesGrid from "./FilesGrid";

import type { Document } from "../Types/Document";
import type { SegmentedControlOption } from "../Ui/SegmentedControl/SegmentedControlOption";

import "./Search.css";

type SearchMode = "text" | "image";

const SEARCH_TYPE_SEGMENTED_CONTROL_OPTIONS: SegmentedControlOption[] = [
  { id: "text", label: "PDFs", icon: FileText },
  { id: "image", label: "Images", icon: Image },
];

function Search() {
  const [query, setQuery] = useState<string>("");
  const [searchMode, setSearchMode] = useState<SearchMode>("text");
  const [files, setFiles] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [shouldShowEmptyState, setShouldShowEmptyState] =
    useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleQueryChange = (value: string) => {
    setQuery(value);
    if (error) {
      setError(null);
    }
  };

  const handleSearch = async () => {
    if (query.length === 0) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setFiles([]);
    setShouldShowEmptyState(false);

    try {
      const response: Response = await apiFetch(
        `/api/documents/search?query=${encodeURIComponent(query)}&search_mode=${searchMode}`,
        {
          method: "GET",
        },
      );

      if (!response.ok) {
        throw new Error("Failed to search");
      }

      const responseJson: Document[] = (await response.json()) as Document[];

      if (responseJson.length === 0) {
        setShouldShowEmptyState(true);
      }

      setFiles(responseJson);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to search");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-container">
      <Header>What are you looking for?</Header>
      <div className="search-bar-container">
        <SearchBar
          value={query}
          onChange={handleQueryChange}
          onSearch={() => void handleSearch()}
          suffix={
            <SegmentedControl
              ariaLabel="Type"
              value={searchMode}
              options={SEARCH_TYPE_SEGMENTED_CONTROL_OPTIONS}
              onChange={(id) => {
                setSearchMode(id as SearchMode);
              }}
            />
          }
        />
      </div>
      <FilesGrid
        files={files}
        isLoading={isLoading}
        shouldShowEmptyState={shouldShowEmptyState}
        error={error}
        retrySearch={() => void handleSearch()}
      />
    </div>
  );
}

export default Search;
