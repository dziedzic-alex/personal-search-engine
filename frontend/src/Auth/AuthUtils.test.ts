import { describe, expect, it } from "vitest";

import { formatSecondsAsTimer, validatePassword } from "./AuthUtils";

describe("formatSecondsAsTimer", () => {
  it("formats zero seconds", () => {
    expect(formatSecondsAsTimer(0)).toBe("0:00");
  });

  it("pads single-digit seconds", () => {
    expect(formatSecondsAsTimer(5)).toBe("0:05");
  });

  it("formats seconds under a minute", () => {
    expect(formatSecondsAsTimer(59)).toBe("0:59");
  });

  it("formats exact minutes", () => {
    expect(formatSecondsAsTimer(60)).toBe("1:00");
  });

  it("formats minutes and seconds", () => {
    expect(formatSecondsAsTimer(125)).toBe("2:05");
  });
});

describe("validatePassword", () => {
  it("rejects passwords that contain spaces", () => {
    expect(validatePassword("pass word", "pass word")).toBe(
      "Password cannot contain spaces",
    );
  });

  it("rejects mismatched passwords", () => {
    expect(validatePassword("password123", "password456")).toBe(
      "Passwords do not match",
    );
  });

  it("returns null for valid matching passwords", () => {
    expect(validatePassword("password123", "password123")).toBeNull();
  });
});
