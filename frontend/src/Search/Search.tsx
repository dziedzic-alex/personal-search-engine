import { useState } from "react";

import "./Search.css";

interface SearchResponse {
  relevant_documents: {
    name: string;
  }[];
}

function Search() {
  const [query, setQuery] = useState<string>("");
  const [responseData, setResponseData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setError(null);
    setResponseData(null);

    const response: Response = await fetch(`/api/search/?query=${query}`, {
      method: "GET",
    });

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
      <button onClick={() => void handleSearch()}>Search</button>
      {error && <p>{error}</p>}
      {responseData && <p>{responseData}</p>}
    </div>
  );
}

export default Search;
