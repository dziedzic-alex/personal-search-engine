import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createMockAuthContext } from "../test/authTest.utils";
import { notify } from "../Ui/Notification/notify";

import ConfirmEmail from "./ConfirmEmail";

import type { AuthContextValue } from "./AuthContext";

const mockVerifyEmail =
  vi.fn<(token: string, userId: string) => Promise<void>>();
const mockUseAuth = vi.fn<() => AuthContextValue>();

vi.mock("./AuthContext", () => ({
  useAuth: (): AuthContextValue => mockUseAuth(),
}));

vi.mock("../Ui/Notification/notify", () => ({
  notify: vi.fn(),
}));

function renderConfirm(search = "?token=abc&user_id=1") {
  return render(
    <MemoryRouter initialEntries={[`/verify-email/confirm${search}`]}>
      <Routes>
        <Route path="/verify-email/confirm" element={<ConfirmEmail />} />
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/" element={<div>Home page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ConfirmEmail", () => {
  beforeEach(() => {
    mockVerifyEmail.mockReset();
    vi.mocked(notify).mockReset();
    mockUseAuth.mockReturnValue(
      createMockAuthContext({ user: null, verifyEmail: mockVerifyEmail }),
    );
  });

  it("redirects to login when token or user_id is missing", () => {
    renderConfirm();

    expect(screen.getByText("Login page")).toBeInTheDocument();
    expect(mockVerifyEmail).not.toHaveBeenCalled();
  });

  it("verifies email and shows success toast", async () => {
    mockVerifyEmail.mockResolvedValue();
    renderConfirm();

    await waitFor(() => {
      expect(mockVerifyEmail).toHaveBeenCalledWith("abc", "1");
    });
    expect(notify).toHaveBeenCalledWith({
      message: "Email verified successfully",
      variant: "success",
    });
  });

  it("shows error toast and navigates to login on failure", async () => {
    mockVerifyEmail.mockRejectedValue(new Error("Invalid or expired link"));
    renderConfirm();

    await waitFor(() => {
      expect(notify).toHaveBeenCalledWith({
        message: "Invalid or expired link",
        variant: "error",
        durationMs: 10000,
      });
    });
    expect(await screen.findByText("Login page")).toBeInTheDocument();
  });
});
