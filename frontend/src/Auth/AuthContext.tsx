import { createContext, use } from "react";

import type { LoginResult } from "./AuthProvider";
import type { User } from "./User";

export interface AuthContextValue {
  user: User | null;
  getAccessToken: () => string | null;
  refreshAccessToken: () => Promise<void>;
  isRefreshingAccessToken: boolean;
  signup: (
    firstName: string,
    lastName: string,
    email: string,
    password: string,
  ) => Promise<string>;
  login: (email: string, password: string) => Promise<LoginResult>;
  logout: () => Promise<void>;
  clearSession: () => void;
  updateUser: (firstName: string, lastName: string) => Promise<void>;
  verifyEmail: (token: string, userId: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const context = use(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}

export function useAuthenticatedUser(): AuthContextValue & { user: User } {
  const context = useAuth();
  if (!context.user) {
    throw new Error(
      "useAuthenticatedUser must be used within an authenticated route",
    );
  }

  return context as AuthContextValue & { user: User };
}
