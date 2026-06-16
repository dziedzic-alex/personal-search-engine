import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { AuthContext } from "../Auth/AuthContext";
import type { User } from "../Auth/User";
import ProtectedRoute from "../ProtectedRoute";

export const mockUser: User = {
  id: 1,
  firstName: "Test",
  email: "test@example.com",
  plan: "free",
};

const baseAuthContext = {
  getAccessToken: () => null,
  refreshAccessToken: async () => {},
  signup: async () => {},
  login: async () => {},
  logout: async () => {},
  clearSession: () => {},
};

export function renderProtectedRoute(
  auth: Partial<{
    user: User | null;
    isRefreshingAccessToken: boolean;
  }>,
) {
  return render(
    <AuthContext
      value={{
        user: null,
        isRefreshingAccessToken: false,
        ...baseAuthContext,
        ...auth,
      }}
    >
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
