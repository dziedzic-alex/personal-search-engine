import { describe, expect, it } from "vitest";

import { passesDateFilter } from "./dateFilter.utils";

describe("passesDateFilter", () => {
  const now = new Date(2025, 5, 17, 15, 0);

  it("matches today", () => {
    expect(passesDateFilter("today", "2025-06-17T10:00:00", now)).toBe(true);
    expect(passesDateFilter("today", "2025-06-16T23:59:00", now)).toBe(false);
  });

  it("matches last 7 calendar days including today", () => {
    expect(passesDateFilter("last7Days", "2025-06-11T08:00:00", now)).toBe(
      true,
    );
    expect(passesDateFilter("last7Days", "2025-06-10T23:59:00", now)).toBe(
      false,
    );
  });

  it("matches last 30 calendar days including today", () => {
    expect(passesDateFilter("last30Days", "2025-05-19T08:00:00", now)).toBe(
      true,
    );
    expect(passesDateFilter("last30Days", "2025-05-18T23:59:00", now)).toBe(
      false,
    );
  });

  it("matches this year and last year", () => {
    expect(passesDateFilter("thisYear", "2025-01-01T00:00:00", now)).toBe(true);
    expect(passesDateFilter("thisYear", "2024-12-31T23:59:00", now)).toBe(
      false,
    );
    expect(passesDateFilter("lastYear", "2024-06-17T10:00:00", now)).toBe(true);
    expect(passesDateFilter("lastYear", "2023-12-31T23:59:00", now)).toBe(
      false,
    );
  });

  it("returns false for null or invalid dates", () => {
    expect(passesDateFilter("today", null, now)).toBe(false);
    expect(passesDateFilter("today", "not-a-date", now)).toBe(false);
  });
});
