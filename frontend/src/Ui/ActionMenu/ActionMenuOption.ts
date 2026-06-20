import type { LucideIcon } from "lucide-react";

export interface ActionMenuOption {
  id: string;
  label: string;
  icon?: LucideIcon;
  iconColor?: string;
  variant?: "default" | "danger";
  onClick: () => void;
  disabled?: boolean;
}
