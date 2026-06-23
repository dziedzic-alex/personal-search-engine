import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createMockAuthContext } from "../test/authTest.utils";

import type { AuthContextValue } from "./AuthContext";

import Login from "./Login";

const mockLogin = vi.fn<(email: string, password: string) => Promise<void>>();
const mockUseAuth = vi.fn<() => AuthContextValue>();

vi.mock("./AuthContext.tsx", () => ({
  useAuth: (): AuthContextValue => mockUseAuth(),
}));

function renderLogin(initialPath = "/login") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<div>Home page</div>} />
      </Routes>
    </MemoryRouter>,
  );
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

  it("calls login with email and password on submit", async () => {
    mockLogin.mockResolvedValue();
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
    });
  });

  it("shows an error when login fails", async () => {
    mockLogin.mockRejectedValue(new Error("Invalid username or password"));
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "wrong-password" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    expect(
      await screen.findByText("Invalid username or password"),
    ).toBeInTheDocument();
  });
});
