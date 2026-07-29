import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import RequestPasswordChange from "./RequestPasswordChange";

function renderRequestPasswordChange() {
  return render(
    <MemoryRouter initialEntries={["/request-password-change"]}>
      <Routes>
        <Route
          path="/request-password-change"
          element={<RequestPasswordChange />}
        />
        <Route path="/login" element={<div>Login page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RequestPasswordChange", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 204 }))),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends password change email and starts cooldown", async () => {
    renderRequestPasswordChange();

    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Send password change email" }),
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/auth/request-password-change", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "test@example.com" }),
      });
    });

    expect(
      await screen.findByRole("button", { name: /Resend in 0:5/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/We sent a password change link to/),
    ).toBeInTheDocument();
  });

  it("shows an error when sending fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 500 }))),
    );
    renderRequestPasswordChange();

    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Send password change email" }),
    );

    expect(
      await screen.findByText(
        "Failed to send password change email. Please try again.",
      ),
    ).toBeInTheDocument();
  });
});
