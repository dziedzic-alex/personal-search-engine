import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { apiFetch, configureApiClient } from "../ApiClient";

import { AuthContext } from "./AuthContext";

import type { User, UserPlan } from "./User";

interface AuthResponse {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  plan: UserPlan;
  accessToken: string;
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  const [user, setUser] = useState<User | null>(null);
  const [isRefreshingAccessToken, setIsRefreshingAccessToken] = useState(true);

  const accessTokenRef = useRef<string | null>(null);
  const refreshAccessTokenRequestRef = useRef<Promise<void> | null>(null);

  const clearSession = useCallback(() => {
    setUser(null);
    accessTokenRef.current = null;
  }, []);

  const navigateToLogin = useCallback(
    () => void navigate("/login", { replace: true }),
    [navigate],
  );

  const getAccessToken = useCallback((): string | null => {
    return accessTokenRef.current;
  }, []);

  const refreshAccessToken = useCallback(async () => {
    refreshAccessTokenRequestRef.current ??= (async () => {
      const response: Response = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Refresh failed");
      }

      const data: AuthResponse = (await response.json()) as AuthResponse;
      setUser({
        id: data.id,
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        plan: data.plan,
      });
      accessTokenRef.current = data.accessToken;
    })()
      .catch((error: unknown) => {
        clearSession();
        throw error;
      })
      .finally(() => {
        refreshAccessTokenRequestRef.current = null;
      });
    await refreshAccessTokenRequestRef.current;
  }, [clearSession]);

  const signup = useCallback(
    async (
      firstName: string,
      lastName: string,
      email: string,
      password: string,
    ) => {
      try {
        const response: Response = await fetch("/api/auth/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            firstName,
            lastName,
            email,
            password,
          }),
        });

        if (response.status === 409) {
          throw new Error("Email already in use");
        } else if (response.status !== 201) {
          throw new Error("Failed to signup. Please try again.");
        }

        const data: AuthResponse = (await response.json()) as AuthResponse;
        setUser({
          id: data.id,
          firstName: data.firstName,
          lastName: data.lastName,
          email: data.email,
          plan: data.plan,
        });
        accessTokenRef.current = data.accessToken;
      } catch (error) {
        clearSession();
        throw error;
      }
    },
    [clearSession],
  );

  const login = useCallback(
    async (email: string, password: string) => {
      try {
        const response: Response = await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email,
            password,
          }),
        });

        if (response.status == 401) {
          throw new Error("Invalid username or password");
        } else if (response.status !== 200) {
          throw new Error("Failed to login. Please try again.");
        }

        const data: AuthResponse = (await response.json()) as AuthResponse;
        setUser({
          id: data.id,
          firstName: data.firstName,
          lastName: data.lastName,
          email: data.email,
          plan: data.plan,
        });
        accessTokenRef.current = data.accessToken;
      } catch (error) {
        clearSession();
        throw error;
      }
    },
    [clearSession],
  );

  const logout = useCallback(async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } finally {
      clearSession();
      navigateToLogin();
    }
  }, [clearSession, navigateToLogin]);

  const updateUser = useCallback(
    async (firstName: string, lastName: string) => {
      const response = await apiFetch("/api/user/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firstName,
          lastName,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update user. Please try again.");
      }

      const data: User = (await response.json()) as User;
      setUser({
        id: data.id,
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        plan: data.plan,
      });
    },
    [],
  );

  const contextValue = useMemo(() => {
    return {
      user,
      getAccessToken,
      refreshAccessToken,
      isRefreshingAccessToken,
      signup,
      login,
      logout,
      clearSession,
      updateUser,
    };
  }, [
    user,
    getAccessToken,
    refreshAccessToken,
    isRefreshingAccessToken,
    signup,
    login,
    logout,
    clearSession,
    updateUser,
  ]);

  useEffect(() => {
    void refreshAccessToken().finally(() => {
      setIsRefreshingAccessToken(false);
    });

    configureApiClient({
      getAccessToken,
      refreshAccessToken,
      clearSession,
      navigateToLogin,
    });
  }, [refreshAccessToken, clearSession, navigateToLogin, getAccessToken]);

  return <AuthContext value={contextValue}>{children}</AuthContext>;
}

export default AuthProvider;
