import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";

import type { ActionMenuOption } from "./ActionMenuOption";

import "./ActionMenu.css";

const ICON_SIZE = 16;
const PANEL_GAP_PX = 4;
const VIEWPORT_PADDING_PX = 8;

interface PanelPosition {
  top: number;
  left: number;
}

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

function computePanelPosition(
  triggerRect: DOMRect,
  panelRect: DOMRect,
): PanelPosition {
  const spaceBelow = window.innerHeight - triggerRect.bottom;
  const spaceAbove = triggerRect.top;
  const openDown =
    spaceBelow >= panelRect.height + PANEL_GAP_PX || spaceBelow >= spaceAbove;

  let top: number;
  if (openDown) {
    top = triggerRect.bottom + PANEL_GAP_PX;
  } else {
    top = triggerRect.top - PANEL_GAP_PX - panelRect.height;
  }

  let left = triggerRect.left - panelRect.width;
  if (left < VIEWPORT_PADDING_PX) {
    left = VIEWPORT_PADDING_PX;
  }

  const maxLeft = window.innerWidth - panelRect.width - VIEWPORT_PADDING_PX;
  if (left > maxLeft) {
    left = maxLeft;
  }

  return { top, left };
}

function applyPanelPosition(
  panel: HTMLUListElement,
  position: PanelPosition,
) {
  panel.style.top = String(position.top) + "px";
  panel.style.left = String(position.left) + "px";
  panel.style.visibility = "visible";
}

function ActionMenu(props: Props) {
  const { renderTrigger, options } = props;

  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLUListElement>(null);
  const menuId = useId();

  useLayoutEffect(() => {
    if (!isOpen) {
      return;
    }

    function updatePanelPosition() {
      if (!containerRef.current || !panelRef.current) {
        return;
      }

      const triggerRect = containerRef.current.getBoundingClientRect();
      const panelRect = panelRef.current.getBoundingClientRect();
      applyPanelPosition(
        panelRef.current,
        computePanelPosition(triggerRect, panelRect),
      );
    }

    updatePanelPosition();
    window.addEventListener("resize", updatePanelPosition);
    window.addEventListener("scroll", updatePanelPosition, true);

    return () => {
      window.removeEventListener("resize", updatePanelPosition);
      window.removeEventListener("scroll", updatePanelPosition, true);
    };
  }, [isOpen, options]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      const target = event.target as Node;

      if (
        containerRef.current?.contains(target) ||
        panelRef.current?.contains(target)
      ) {
        return;
      }

      setIsOpen(false);
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

  const panel =
    isOpen &&
    createPortal(
      <ul
        id={menuId}
        ref={panelRef}
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
      </ul>,
      document.body,
    );

  return (
    <div className="action-menu" ref={containerRef}>
      {renderTrigger(triggerProps)}
      {panel}
    </div>
  );
}

export default ActionMenu;
