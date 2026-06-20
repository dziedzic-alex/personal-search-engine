export type NotificationVariant = "error" | "success" | "info";

export interface NotificationItem {
  id: string;
  message: string;
  variant: NotificationVariant;
  durationMs: number;
}

export interface NotifyOptions {
  message: string;
  variant?: NotificationVariant;
  durationMs?: number;
}

export const DEFAULT_NOTIFICATION_DURATION_MS = 5000;
