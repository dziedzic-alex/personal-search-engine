import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Signup from "./Signup";
import { mockUser } from "../test/authTestUtils";

const mockSignup =
  vi.fn<
    (
      firstName: string,
      lastName: string,
      email: string,
      password: string,
    ) => Promise<void>
  >();
const mockUseAuth = vi.fn();

vi.mock("./AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

function renderSignup(initialPath = "/signup") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<div>Home page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function fillSignupForm() {
  fireEvent.change(screen.getByPlaceholderText("First Name"), {
    target: { value: "Test" },
  });
  fireEvent.change(screen.getByPlaceholderText("Last Name"), {
    target: { value: "User" },
  });
  fireEvent.change(screen.getByPlaceholderText("Email"), {
    target: { value: "test@example.com" },
  });
  fireEvent.change(screen.getByPlaceholderText("Password"), {
    target: { value: "password123" },
  });
  fireEvent.change(screen.getByPlaceholderText("Confirm Password"), {
    target: { value: "password123" },
  });
}

describe("Signup", () => {
  beforeEach(() => {
    mockSignup.mockReset();
    mockUseAuth.mockReturnValue({
      user: null,
      signup: mockSignup,
    });
  });

  it("renders the signup form", () => {
    renderSignup();

    expect(screen.getByRole("heading", { name: "Signup" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("First Name")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Confirm Password")).toBeInTheDocument();
  });

  it("calls signup with form values on submit", async () => {
    mockSignup.mockResolvedValue();
    renderSignup();
    fillSignupForm();
    fireEvent.click(screen.getByRole("button", { name: "Signup" }));

    await waitFor(() => {
      expect(mockSignup).toHaveBeenCalledWith(
        "Test",
        "User",
        "test@example.com",
        "password123",
      );
    });
  });

  it("shows an error when signup fails", async () => {
    mockSignup.mockRejectedValue(new Error("Email already in use"));
    renderSignup();
    fillSignupForm();
    fireEvent.click(screen.getByRole("button", { name: "Signup" }));

    expect(await screen.findByText("Email already in use")).toBeInTheDocument();
  });

  it("shows validation error when passwords do not match", async () => {
    renderSignup();
    fillSignupForm();
    fireEvent.change(screen.getByPlaceholderText("Confirm Password"), {
      target: { value: "different-password" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Signup" }));

    expect(
      await screen.findByText("Passwords do not match"),
    ).toBeInTheDocument();
    expect(mockSignup).not.toHaveBeenCalled();
  });

  it("redirects to home when user is already authenticated", () => {
    mockUseAuth.mockReturnValue({
      user: mockUser,
      signup: mockSignup,
    });

    renderSignup();

    expect(screen.getByText("Home page")).toBeInTheDocument();
  });
});
