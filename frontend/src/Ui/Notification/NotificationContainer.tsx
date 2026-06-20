import { createPortal } from "react-dom";

import Notification from "./Notification";

import type { NotificationItem } from "./notification.types";

import "./NotificationContainer.css";

interface Props {
  notifications: NotificationItem[];
  onDismiss: (id: string) => void;
}

function NotificationContainer(props: Props) {
  const { notifications, onDismiss } = props;

  if (notifications.length === 0) {
    return null;
  }

  return createPortal(
    <div className="notification-container" aria-live="polite">
      {notifications.map((notification) => (
        <Notification
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
        />
      ))}
    </div>,
    document.body,
  );
}

export default NotificationContainer;
