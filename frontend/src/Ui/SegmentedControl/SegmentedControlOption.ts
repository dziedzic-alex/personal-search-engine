import type { LucideIcon } from "lucide-react";

export interface SegmentedControlOption {
  id: string;
  label: string;
  icon?: LucideIcon;
  iconColor?: string;
  disabled?: boolean;
}
