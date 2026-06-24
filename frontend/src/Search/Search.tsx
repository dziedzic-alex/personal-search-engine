import { FileText, Image } from "lucide-react";
import { useState } from "react";

import { apiFetch } from "../ApiClient";
import SearchBar from "../Ui/SearchBar/SearchBar";
import SegmentedControl from "../Ui/SegmentedControl/SegmentedControl";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import type { SegmentedControlOption } from "../Ui/SegmentedControl/SegmentedControlOption";

import "./Search.css";

type SearchMode = "text" | "image";

interface SearchResponse {
  relevant_documents: {
    name: string;
  }[];
}

const SEARCH_TYPE_SEGMENTED_CONTROL_OPTIONS: SegmentedControlOption[] = [
  { id: "text", label: "PDFs", icon: FileText },
  { id: "image", label: "Images", icon: Image },
];

function Search() {
  const [query, setQuery] = useState<string>("");
  const [searchMode, setSearchMode] = useState<SearchMode>("text");
  const [responseData, setResponseData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQueryChange = (value: string) => {
    setQuery(value);
    if (error) {
      setError(null);
    }
    if (responseData) {
      setResponseData(null);
    }
  };

  const handleSearch = async () => {
    setError(null);
    setResponseData(null);

    try {
      const response: Response = await apiFetch(
        `/api/search/?query=${query}&search_mode=${searchMode}`,
        {
          method: "GET",
        },
      );

      if (!response.ok) {
        throw new Error("Failed to search");
      }

      const responseJson: SearchResponse =
        (await response.json()) as SearchResponse;

      setResponseData(JSON.stringify(responseJson));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to search");
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
      {error && <Body variant="error">{error}</Body>}
      {responseData && <Body variant="muted">{responseData}</Body>}
    </div>
  );
}

export default Search;
