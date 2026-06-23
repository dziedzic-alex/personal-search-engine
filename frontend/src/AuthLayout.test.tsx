import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { mockUser, renderAuthLayout } from "./test/authTest.utils";

vi.mock("./Navbar/Navbar.tsx", () => ({
  default: () => <nav>Navbar</nav>,
}));

describe("AuthLayout", () => {
  it("shows loading while refreshing access token", () => {
    renderAuthLayout({
      user: null,
      isRefreshingAccessToken: true,
    });

    expect(screen.getByRole("status", { name: "Loading" })).toBeInTheDocument();
    expect(screen.getByText("Navbar")).toBeInTheDocument();
  });

  it("redirects to home when user is already authenticated", () => {
    renderAuthLayout({
      user: mockUser,
      isRefreshingAccessToken: false,
    });

    expect(screen.getByText("Home page")).toBeInTheDocument();
  });

  it("renders auth page content when unauthenticated", () => {
    renderAuthLayout({
      user: null,
      isRefreshingAccessToken: false,
    });

    expect(screen.getByText("Login page")).toBeInTheDocument();
    expect(screen.getByText("Navbar")).toBeInTheDocument();
  });
});
