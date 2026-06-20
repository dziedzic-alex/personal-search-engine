export function formatDate(
  date: string | Date,
  now: Date = new Date(),
): string {
  const value = typeof date === "string" ? new Date(date) : date;

  if (isSameDay(value, now)) {
    return formatTime(value);
  }

  if (isSameYear(value, now)) {
    return value.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  }

  return value.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
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

function formatTime(date: Date): string {
  const minutes = date.getMinutes().toString().padStart(2, "0");
  let hours = date.getHours();
  const meridiem = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;

  if (hours === 0) {
    hours = 12;
  }

  return `${hours.toString()}:${minutes} ${meridiem}`;
}
