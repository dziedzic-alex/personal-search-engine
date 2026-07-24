import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createMockAuthContext } from "../test/authTest.utils";

import Login from "./Login";

import type { AuthContextValue } from "./AuthContext";
import type { LoginResult } from "./AuthProvider";

const mockLogin =
  vi.fn<(email: string, password: string) => Promise<LoginResult>>();
const mockUseAuth = vi.fn<() => AuthContextValue>();

vi.mock("./AuthContext.tsx", () => ({
  useAuth: (): AuthContextValue => mockUseAuth(),
}));

function renderLogin(initialPath = "/login") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/verify-email" element={<div>Verify email page</div>} />
        <Route path="/" element={<div>Home page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function fillLoginForm() {
  fireEvent.change(screen.getByPlaceholderText("Email"), {
    target: { value: "test@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText("Password"), {
    target: { value: "password123" },
  });
}

describe("Login", () => {
  beforeEach(() => {
    mockLogin.mockReset();
    mockUseAuth.mockReturnValue(
      createMockAuthContext({ user: null, login: mockLogin }),
    );
  });

  it("renders the login form", () => {
    renderLogin();

    expect(screen.getByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
  });

  it("calls login and navigates home when authenticated", async () => {
    mockLogin.mockResolvedValue("authenticated");
    renderLogin();
    fillLoginForm();
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
    });
    expect(await screen.findByText("Home page")).toBeInTheDocument();
  });

  it("navigates to verify-email when email is not verified", async () => {
    mockLogin.mockResolvedValue("email_not_verified");
    renderLogin();
    fillLoginForm();
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    expect(await screen.findByText("Verify email page")).toBeInTheDocument();
  });

  it("shows an error when login fails", async () => {
    mockLogin.mockRejectedValue(new Error("Invalid username or password"));
    renderLogin();
    fillLoginForm();
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "wrong-password" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    expect(
      await screen.findByText("Invalid username or password"),
    ).toBeInTheDocument();
  });
});
