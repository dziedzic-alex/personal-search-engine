export type DateFilterOption =
  | "today"
  | "last7Days"
  | "last30Days"
  | "thisYear"
  | "lastYear";

export function passesDateFilter(
  dateFilter: DateFilterOption,
  date: string | null,
  now: Date = new Date(),
): boolean {
  if (date === null) {
    return false;
  }

  const dateValue = new Date(date);

  if (Number.isNaN(dateValue.getTime())) {
    return false;
  }

  switch (dateFilter) {
    case "today":
      return isSameDay(dateValue, now);
    case "last7Days":
      return isWithinLastDays(dateValue, 7, now);
    case "last30Days":
      return isWithinLastDays(dateValue, 30, now);
    case "thisYear":
      return isSameYear(dateValue, now);
    case "lastYear":
      return isLastYear(dateValue, now);
  }
}

function isLastYear(date: Date, now: Date): boolean {
  return date.getFullYear() === now.getFullYear() - 1;
}

function isWithinLastDays(date: Date, days: number, now: Date): boolean {
  const value = startOfDay(date);
  const cutoff = startOfDay(now);
  cutoff.setDate(cutoff.getDate() - (days - 1));

  return value >= cutoff && value <= startOfDay(now);
}

function startOfDay(date: Date): Date {
  const value = new Date(date);
  value.setHours(0, 0, 0, 0);
  return value;
}

function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

function isSameYear(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear();
}
