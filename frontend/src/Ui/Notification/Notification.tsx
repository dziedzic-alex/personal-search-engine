import { CircleCheck, CircleX, Info, X } from "lucide-react";
import { useEffect } from "react";

import type {
  NotificationItem,
  NotificationVariant,
} from "./notification.types";

import "./Notification.css";

const DISMISS_ICON_SIZE = 16;
const VARIANT_ICON_SIZE = 22;

interface Props {
  notification: NotificationItem;
  onDismiss: (id: string) => void;
}

function getVariantIcon(variant: NotificationVariant) {
  switch (variant) {
    case "success":
      return (
        <CircleCheck
          size={VARIANT_ICON_SIZE}
          color="#3d6b4a"
          aria-hidden
        />
      );
    case "error":
      return (
        <CircleX size={VARIANT_ICON_SIZE} color="#8b4a42" aria-hidden />
      );
    case "info":
      return (
        <Info
          size={VARIANT_ICON_SIZE}
          color="var(--color-accent)"
          aria-hidden
        />
      );
  }
}

function Notification(props: Props) {
  const { notification, onDismiss } = props;
  const { id, message, variant, durationMs } = notification;

  useEffect(() => {
    const timer = window.setTimeout(() => {
      onDismiss(id);
    }, durationMs);

    return () => {
      window.clearTimeout(timer);
    };
  }, [durationMs, id, onDismiss]);

  return (
    <div
      className={["notification", `notification-${variant}`].join(" ")}
      role={variant === "error" ? "alert" : "status"}
    >
      <div className="notification-content">
        <span className="notification-icon">{getVariantIcon(variant)}</span>
        <p className="notification-message">{message}</p>
      </div>
      <button
        type="button"
        className="notification-dismiss"
        aria-label="Dismiss notification"
        onClick={() => {
          onDismiss(id);
        }}
      >
        <X size={DISMISS_ICON_SIZE} aria-hidden />
      </button>
    </div>
  );
}

export default Notification;
