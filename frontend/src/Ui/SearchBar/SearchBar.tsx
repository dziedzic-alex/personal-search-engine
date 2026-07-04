import { ScanSearch, X } from "lucide-react";

import IconButton from "../Buttons/IconButton";
import TextInput from "../TextInput/TextInput";

import type { ReactNode } from "react";

import "./SearchBar.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
  isDisabled?: boolean;
  suffix?: ReactNode;
  onFocus?: () => void;
  onBlur?: () => void;
  inputRef?: React.Ref<HTMLInputElement>;
}

function SearchBar(props: Props) {
  const {
    value,
    onChange,
    onSearch,
    placeholder = "Search",
    isDisabled = false,
    suffix,
    onFocus,
    onBlur,
    inputRef,
  } = props;

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
        isDisabled={isDisabled}
        inputMode="search"
        enterKeyHint="search"
        onFocus={onFocus}
        onBlur={onBlur}
        inputRef={inputRef}
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
