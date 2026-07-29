import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { notify } from "../Ui/Notification/notify";

import ResetPassword from "./ResetPassword";

vi.mock("../Ui/Notification/notify", () => ({
  notify: vi.fn(),
}));

function renderResetPassword(search = "?token=abc&user_id=1") {
  return render(
    <MemoryRouter initialEntries={[`/reset-password${search}`]}>
      <Routes>
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/login" element={<div>Login page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function fillPasswords(password = "password123", confirm = "password123") {
  fireEvent.change(screen.getByPlaceholderText("Password"), {
    target: { value: password },
  });
  fireEvent.change(screen.getByPlaceholderText("Confirm Password"), {
    target: { value: confirm },
  });
}

describe("ResetPassword", () => {
  beforeEach(() => {
    vi.mocked(notify).mockReset();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 204 }))),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("redirects to login when user id is missing", () => {
    renderResetPassword("?token=abc");

    expect(screen.getByText("Login page")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("redirects to login when token is missing", () => {
    renderResetPassword("?user_id=1");

    expect(screen.getByText("Login page")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("shows validation error when passwords do not match", async () => {
    renderResetPassword();
    fillPasswords("password123", "different-password");
    fireEvent.click(screen.getByRole("button", { name: "Reset Password" }));

    expect(
      await screen.findByText("Passwords do not match"),
    ).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("resets password, shows success toast, and navigates to login", async () => {
    renderResetPassword();
    fillPasswords();
    fireEvent.click(screen.getByRole("button", { name: "Reset Password" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: "abc",
          userId: "1",
          newPassword: "password123",
        }),
      });
    });

    expect(notify).toHaveBeenCalledWith({
      message:
        "Password reset successfully. Please login with your new password.",
      variant: "success",
    });
    expect(await screen.findByText("Login page")).toBeInTheDocument();
  });

  it("shows an error for expired reset links", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 400 }))),
    );
    renderResetPassword();
    fillPasswords();
    fireEvent.click(screen.getByRole("button", { name: "Reset Password" }));

    expect(
      await screen.findByText(
        "Invalid or expired URL. Please request another password reset.",
      ),
    ).toBeInTheDocument();
  });

  it("shows an error when user is not found", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 404 }))),
    );
    renderResetPassword();
    fillPasswords();
    fireEvent.click(screen.getByRole("button", { name: "Reset Password" }));

    expect(
      await screen.findByText(
        "User associated with URL not found. Please ensure you have an account and try again.",
      ),
    ).toBeInTheDocument();
  });
});
