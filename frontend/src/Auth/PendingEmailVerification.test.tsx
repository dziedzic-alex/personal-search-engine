import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import PendingEmailVerification from "./PendingEmailVerification";

function renderPending(state: unknown = "test@example.com") {
  return render(
    <MemoryRouter initialEntries={[{ pathname: "/verify-email", state }]}>
      <Routes>
        <Route path="/verify-email" element={<PendingEmailVerification />} />
        <Route path="/login" element={<div>Login page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PendingEmailVerification", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 204 }))),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("redirects to login when email state is missing", () => {
    renderPending(null);

    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("sends verification email and starts cooldown", async () => {
    renderPending();

    fireEvent.click(
      screen.getByRole("button", { name: "Send verification email" }),
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/auth/send-verification-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "test@example.com" }),
      });
    });

    expect(
      await screen.findByRole("button", { name: /Resend in 0:5/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/We sent a verification link to/),
    ).toBeInTheDocument();
  });

  it("shows an error when sending fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 500 }))),
    );
    renderPending();

    fireEvent.click(
      screen.getByRole("button", { name: "Send verification email" }),
    );

    expect(
      await screen.findByText(
        "Failed to send verification email. Please try again.",
      ),
    ).toBeInTheDocument();
  });
});
