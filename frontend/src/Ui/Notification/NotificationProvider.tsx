import { useCallback, useEffect, useState } from "react";

import {
  DEFAULT_NOTIFICATION_DURATION_MS,
  type NotificationItem,
  type NotifyOptions,
} from "./notification.types";
import NotificationContainer from "./NotificationContainer";
import { registerNotificationHandlers } from "./notify";

interface Props {
  children: React.ReactNode;
}

function NotificationProvider(props: Props) {
  const { children } = props;

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const dismiss = useCallback((id: string) => {
    setNotifications((current) =>
      current.filter((notification) => notification.id !== id),
    );
  }, []);

  const notify = useCallback((options: NotifyOptions) => {
    const id = crypto.randomUUID();
    const notification: NotificationItem = {
      id,
      message: options.message,
      variant: options.variant ?? "info",
      durationMs: options.durationMs ?? DEFAULT_NOTIFICATION_DURATION_MS,
    };

    setNotifications((current) => [...current, notification]);

    return id;
  }, []);

  useEffect(() => {
    registerNotificationHandlers({ notify, dismiss });

    return () => {
      registerNotificationHandlers(null);
    };
  }, [notify, dismiss]);

  return (
    <>
      {children}
      <NotificationContainer
        notifications={notifications}
        onDismiss={dismiss}
      />
    </>
  );
}

export default NotificationProvider;
