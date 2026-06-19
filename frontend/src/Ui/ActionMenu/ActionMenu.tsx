import { useEffect, useId, useRef, useState } from "react";

import type { ActionMenuOption } from "./ActionMenuOption";

import "./ActionMenu.css";

const ICON_SIZE = 16;

export interface ActionMenuTriggerProps {
  onClick: () => void;
  "aria-haspopup": "menu";
  "aria-expanded": boolean;
  "aria-controls": string;
}

interface Props {
  renderTrigger: (props: ActionMenuTriggerProps) => React.ReactNode;
  options: ActionMenuOption[];
}

function ActionMenu(props: Props) {
  const { renderTrigger, options } = props;

  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const menuId = useId();

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

  function handleSelect(option: ActionMenuOption) {
    if (option.disabled) {
      return;
    }

    option.onClick();
    setIsOpen(false);
  }

  const triggerProps: ActionMenuTriggerProps = {
    onClick: () => {
      setIsOpen((open) => !open);
    },
    "aria-haspopup": "menu",
    "aria-expanded": isOpen,
    "aria-controls": menuId,
  };

  return (
    <div className="action-menu" ref={containerRef}>
      {renderTrigger(triggerProps)}
      {isOpen && (
        <ul
          id={menuId}
          className="action-menu-panel"
          role="menu"
          aria-label="Actions"
        >
          {options.map((option) => {
            const Icon = option.icon;
            const isDanger = option.variant === "danger";
            const iconColor =
              option.iconColor ??
              (isDanger ? "currentColor" : "var(--color-text-muted)");

            return (
              <li key={option.id} role="presentation">
                <button
                  type="button"
                  className={[
                    "action-menu-item",
                    isDanger ? "action-menu-item-danger" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  role="menuitem"
                  disabled={option.disabled}
                  onClick={() => {
                    handleSelect(option);
                  }}
                >
                  {Icon ? (
                    <span className="action-menu-item-icon">
                      <Icon size={ICON_SIZE} aria-hidden color={iconColor} />
                    </span>
                  ) : null}
                  {option.label}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default ActionMenu;
