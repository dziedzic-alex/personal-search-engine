import { createContext, use } from "react";
import type { User } from "./User";

interface AuthContextValue {
  user: User | null;
  getAccessToken: () => string | null;
  refreshAccessToken: () => Promise<void>;
  isRefreshingAccessToken: boolean;
  signup: (
    firstName: string,
    lastName: string,
    email: string,
    password: string,
  ) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearSession: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const context = use(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
