import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi } from "vitest";

import { AuthContext } from "../Auth/AuthContext";
import AuthLayout from "../AuthLayout";
import ProtectedRoute from "../ProtectedRoute";

import type { AuthContextValue } from "../Auth/AuthContext";
import type { User } from "../Auth/User";

export const mockUser: User = {
  id: 1,
  firstName: "Test",
  lastName: "User",
  email: "test@example.com",
  plan: "free",
};

const baseAuthContext: Omit<
  AuthContextValue,
  "user" | "isRefreshingAccessToken"
> = {
  getAccessToken: vi.fn<() => string | null>(() => null),
  refreshAccessToken: vi.fn<() => Promise<void>>(() => Promise.resolve()),
  signup: vi.fn<() => Promise<void>>(() => Promise.resolve()),
  login: vi.fn<() => Promise<void>>(() => Promise.resolve()),
  logout: vi.fn<() => Promise<void>>(() => Promise.resolve()),
  clearSession: vi.fn<() => void>(() => undefined),
  updateUser: vi.fn<() => Promise<void>>(() => Promise.resolve()),
};

export function createMockAuthContext(
  overrides: Partial<AuthContextValue> = {},
): AuthContextValue {
  return {
    user: null,
    isRefreshingAccessToken: false,
    ...baseAuthContext,
    ...overrides,
  };
}

export function renderProtectedRoute(
  auth: Partial<{
    user: User | null;
    isRefreshingAccessToken: boolean;
  }>,
) {
  return render(
    <AuthContext value={createMockAuthContext(auth)}>
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<div>Home content</div>} />
          </Route>
          <Route path="/login" element={<div>Login page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext>,
  );
}

export function renderAuthLayout(
  auth: Partial<{
    user: User | null;
    isRefreshingAccessToken: boolean;
  }>,
  initialPath = "/login",
) {
  return render(
    <AuthContext value={createMockAuthContext(auth)}>
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<div>Login page</div>} />
            <Route path="/signup" element={<div>Signup page</div>} />
          </Route>
          <Route path="/" element={<div>Home page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext>,
  );
}
