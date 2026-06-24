import { ScanSearch, X } from "lucide-react";

import IconButton from "../IconButton";
import TextInput from "../TextInput/TextInput";

import type { ReactNode } from "react";

import "./SearchBar.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
  suffix?: ReactNode;
}

function SearchBar(props: Props) {
  const { value, onChange, onSearch, placeholder = "Search", suffix } = props;

  return (
    <div className="search-bar">
      <IconButton
        className="search-bar-icon"
        ariaLabel="Search"
        onClick={onSearch}
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
      {suffix ? <div className="search-bar-suffix">{suffix}</div> : null}
      <IconButton
        className={[
          "search-bar-clear",
          value.length === 0 ? "search-bar-clear-hidden" : "",
        ]
          .filter(Boolean)
          .join(" ")}
        ariaLabel="Clear search"
        aria-hidden={value.length === 0}
        onClick={() => {
          onChange("");
        }}
      >
        <X />
      </IconButton>
    </div>
  );
}

export default SearchBar;
