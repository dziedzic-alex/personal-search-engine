import { useState } from "react";

import Stack from "../Ui/Layout/Stack";
import SearchBar from "../Ui/SearchBar/SearchBar";

import MyFilesCard from "./MyFilesCard";

import "./Files.css";

function Files() {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentlyExecutedSearchQuery, setCurrentlyExecutedSearchQuery] =
    useState<string | null>(null);

  const handleSearch = () => {
    setCurrentlyExecutedSearchQuery(
      searchQuery.length > 0 ? searchQuery : null,
    );
  };

  const clearSearch = () => {
    setSearchQuery("");
    setCurrentlyExecutedSearchQuery(null);
  };

  return (
    <Stack spacing="md" className="files-container">
      <SearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={handleSearch}
        placeholder="Search by file name"
      />
      <MyFilesCard
        currentlyExecutedSearchQuery={currentlyExecutedSearchQuery}
        clearSearch={clearSearch}
      />
    </Stack>
  );
}

export default Files;
