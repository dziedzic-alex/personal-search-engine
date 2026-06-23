import { Check, ChevronDown } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import type { DropdownOption } from "./DropdownOption";

import "../Button.css";
import "./Dropdown.css";

const ICON_SIZE = 16;

interface Props {
  label: string;
  value: string | null;
  options: DropdownOption[];
  onChange: (id: string) => void;
  isDisabled?: boolean;
}

function Dropdown(props: Props) {
  const { label, value, options, onChange, isDisabled = false } = props;

  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const listboxId = useId();

  const selectedOption = options.find((option) => option.id === value);
  const triggerLabel = selectedOption
    ? `${label}: ${selectedOption.label}`
    : label;

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  function handleSelect(option: DropdownOption) {
    if (option.disabled) {
      return;
    }

    onChange(option.id);
    setIsOpen(false);
  }

  return (
    <div className="dropdown" ref={containerRef}>
      <button
        type="button"
        className="dropdown-trigger button-secondary button-size-small"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        disabled={isDisabled}
        onClick={() => {
          setIsOpen((open) => !open);
        }}
      >
        {triggerLabel}
        <ChevronDown size={14} className="dropdown-trigger-icon" aria-hidden />
      </button>
      {isOpen && (
        <ul
          id={listboxId}
          className="dropdown-menu"
          role="listbox"
          aria-label={label}
        >
          {options.map((option) => {
            const isSelected = value === option.id;

            return (
              <li key={option.id} role="presentation">
                <button
                  type="button"
                  className={[
                    "dropdown-option",
                    isSelected ? "dropdown-option-selected" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  role="option"
                  aria-selected={isSelected}
                  disabled={option.disabled}
                  onClick={() => {
                    handleSelect(option);
                  }}
                >
                  {option.icon ? (
                    <span className="dropdown-option-icon">
                      <option.icon
                        size={ICON_SIZE}
                        aria-hidden
                        color={option.iconColor ?? "var(--color-text-muted)"}
                      />
                    </span>
                  ) : null}
                  {option.label}
                  {isSelected ? (
                    <Check size={14} className="dropdown-option-check" />
                  ) : null}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default Dropdown;
