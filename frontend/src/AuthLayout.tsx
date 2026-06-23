import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "./Auth/AuthContext.tsx";
import Navbar from "./Navbar/Navbar.tsx";
import AppShell from "./Ui/Layout/AppShell.tsx";
import LoadingPage from "./Ui/LoadingPage/LoadingPage.tsx";

function AuthLayout() {
  const { user, isRefreshingAccessToken } = useAuth();

  if (isRefreshingAccessToken) {
    return (
      <AppShell navbar={<Navbar variant="notauthed" />}>
        <LoadingPage />
      </AppShell>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return (
    <AppShell navbar={<Navbar variant="notauthed" />}>
      <Outlet />
    </AppShell>
  );
}

export default AuthLayout;
