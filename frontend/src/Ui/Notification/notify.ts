import type { NotifyOptions } from "./notification.types";

type NotifyFn = (options: NotifyOptions) => string;
type DismissFn = (id: string) => void;

let notifyFn: NotifyFn | null = null;
let dismissFn: DismissFn | null = null;

export function registerNotificationHandlers(
  handlers: { notify: NotifyFn; dismiss: DismissFn } | null,
): void {
  if (handlers === null) {
    notifyFn = null;
    dismissFn = null;
    return;
  }

  notifyFn = handlers.notify;
  dismissFn = handlers.dismiss;
}

export function notify(options: NotifyOptions): string {
  if (notifyFn === null) {
    return "";
  }

  return notifyFn(options);
}

export function dismissNotification(id: string): void {
  dismissFn?.(id);
}
