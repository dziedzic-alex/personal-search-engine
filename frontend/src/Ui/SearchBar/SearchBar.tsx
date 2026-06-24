import { ScanSearch, X } from "lucide-react";

import IconButton from "../IconButton";
import TextInput from "../TextInput/TextInput";

import "./SearchBar.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
}

function SearchBar(props: Props) {
  const { value, onChange, onSearch, placeholder = "Search" } = props;

  return (
    <div className="search-bar">
      <IconButton
        className="search-bar-icon"
        ariaLabel="Search"
        onClick={onSearch}
        size="small"
      >
        <ScanSearch />
      </IconButton>
      <TextInput
        className="search-bar-input"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onEnter={onSearch}
        inputMode="search"
        enterKeyHint="search"
      />
      {value.length > 0 && (
        <IconButton
          className="search-bar-clear"
          ariaLabel="Clear search"
          onClick={() => {
            onChange("");
          }}
          size="small"
        >
          <X />
        </IconButton>
      )}
    </div>
  );
}

export default SearchBar;
