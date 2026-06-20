import { describe, expect, it } from "vitest";

import { formatDate } from "./Date";

describe("formatDate", () => {
  const now = new Date(2025, 5, 17, 15, 30);

  it("formats same-day dates as time", () => {
    expect(formatDate(new Date(2025, 5, 17, 10, 10), now)).toBe("10:10 AM");
    expect(formatDate(new Date(2025, 5, 17, 0, 5), now)).toBe("12:05 AM");
    expect(formatDate(new Date(2025, 5, 17, 15, 30), now)).toBe("3:30 PM");
  });

  it("formats same-year dates as month and day", () => {
    expect(formatDate(new Date(2025, 0, 21), now)).toBe("Jan 21");
  });

  it("formats different-year dates with year", () => {
    expect(formatDate(new Date(2024, 11, 21), now)).toBe("Dec 21, 2024");
  });
});
