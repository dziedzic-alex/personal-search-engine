import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { mockUser, renderProtectedRoute } from "./test/authTest.utils";

vi.mock("./Navbar/Navbar.tsx", () => ({
  default: () => <nav>Navbar</nav>,
}));

describe("ProtectedRoute", () => {
  it("shows loading while refreshing access token", () => {
    renderProtectedRoute({
      user: null,
      isRefreshingAccessToken: true,
    });

    expect(screen.getByRole("status", { name: "Loading" })).toBeInTheDocument();
  });

  it("redirects to login when unauthenticated", () => {
    renderProtectedRoute({
      user: null,
      isRefreshingAccessToken: false,
    });

    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("renders protected content when authenticated", () => {
    renderProtectedRoute({
      user: mockUser,
      isRefreshingAccessToken: false,
    });

    expect(screen.getByText("Home content")).toBeInTheDocument();
    expect(screen.getByText("Navbar")).toBeInTheDocument();
  });
});
