import { describe, expect, it } from "vitest";

import { formatBytes } from "./Bytes";

describe("formatBytes", () => {
  it("formats bytes as KB below 1 MB", () => {
    expect(formatBytes(0)).toBe("0 KB");
    expect(formatBytes(1536)).toBe("1.5 KB");
    expect(formatBytes(1048575)).toBe("1024 KB");
  });

  it("formats bytes as MB below 1 GB", () => {
    expect(formatBytes(1048576)).toBe("1 MB");
    expect(formatBytes(1572864)).toBe("1.5 MB");
  });

  it("formats bytes as GB at 1 GB and above", () => {
    expect(formatBytes(1073741824)).toBe("1 GB");
    expect(formatBytes(1610612736)).toBe("1.5 GB");
  });
});
