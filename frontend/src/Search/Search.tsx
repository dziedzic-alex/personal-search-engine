import { useState } from "react";

import "./Search.css";

type SearchMode = "text" | "image";

interface SearchResponse {
  relevant_documents: {
    name: string;
  }[];
}

function Search() {
  const [query, setQuery] = useState<string>("");
  const [searchMode, setSearchMode] = useState<SearchMode>("text");
  const [responseData, setResponseData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setError(null);
    setResponseData(null);

    const response: Response = await fetch(
      `/api/search/?query=${query}&search_mode=${searchMode}`,
      {
        method: "GET",
      },
    );

    if (!response.ok) {
      setError("Failed to search");
      return;
    }

    const responseJson: SearchResponse =
      (await response.json()) as SearchResponse;

    setResponseData(JSON.stringify(responseJson));
  };

  return (
    <div className="search">
      <textarea
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          if (error) {
            setError(null);
          }
          if (responseData) {
            setResponseData(null);
          }
        }}
      />
      <select
        value={searchMode}
        onChange={(e) => {
          setSearchMode(e.target.value as SearchMode);
        }}
      >
        <option value="text">Text based documents</option>
        <option value="image">Image based documents</option>
      </select>
      <button onClick={() => void handleSearch()}>Search</button>
      {error && <p>{error}</p>}
      {responseData && <p>{responseData}</p>}
    </div>
  );
}

export default Search;
