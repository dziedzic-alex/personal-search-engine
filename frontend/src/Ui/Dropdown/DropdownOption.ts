import type { LucideIcon } from "lucide-react";

export interface DropdownOption {
  id: string;
  label: string;
  icon?: LucideIcon;
  iconColor?: string;
  disabled?: boolean;
}
