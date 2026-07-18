import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthContext } from "../Auth/AuthContext";
import { createMockAuthContext, mockUser } from "../test/authTest.utils";

import Profile from "./Profile";

import type { AuthContextValue } from "../Auth/AuthContext";

const mockNotify =
  vi.fn<(args: { message: string; variant: string }) => void>();

vi.mock("../Ui/Notification/notify", () => ({
  notify: (args: { message: string; variant: string }) => {
    mockNotify(args);
  },
}));

function renderProfile(overrides: Partial<AuthContextValue> = {}) {
  const authContext = createMockAuthContext({
    user: mockUser,
    ...overrides,
  });

  render(
    <AuthContext value={authContext}>
      <Profile />
    </AuthContext>,
  );

  return authContext;
}

describe("Profile", () => {
  beforeEach(() => {
    mockNotify.mockReset();
  });

  it("calls updateUser and shows notification on successful save", async () => {
    const authContext = renderProfile();

    const firstNameInput = screen.getByDisplayValue("Test");
    await userEvent.clear(firstNameInput);
    await userEvent.type(firstNameInput, "Updated");

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(authContext.updateUser).toHaveBeenCalledWith("Updated", "User");
    });

    expect(mockNotify).toHaveBeenCalledWith({
      message: "Account updated successfully.",
      variant: "success",
    });
  });

  it("displays an error when updateUser fails", async () => {
    const authContext = renderProfile({
      updateUser: vi.fn(() => Promise.reject(new Error("Network error"))),
    });

    const lastNameInput = screen.getByDisplayValue("User");
    await userEvent.clear(lastNameInput);
    await userEvent.type(lastNameInput, "Changed");

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(authContext.updateUser).toHaveBeenCalledWith("Test", "Changed");
    });

    expect(screen.getByText("Network error")).toBeInTheDocument();
    expect(mockNotify).not.toHaveBeenCalled();
  });
});
