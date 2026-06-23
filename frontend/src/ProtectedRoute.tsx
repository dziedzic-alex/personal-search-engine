import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "./Auth/AuthContext.tsx";
import Navbar from "./Navbar/Navbar.tsx";
import AppShell from "./Ui/Layout/AppShell.tsx";
import LoadingPage from "./Ui/LoadingPage/LoadingPage.tsx";

function ProtectedRoute() {
  const { user, isRefreshingAccessToken } = useAuth();

  if (!user && isRefreshingAccessToken) {
    return (
      <AppShell>
        <LoadingPage />
      </AppShell>
    );
  } else if (!user && !isRefreshingAccessToken) {
    return <Navigate to="/login" replace />;
  }

  return (
    <AppShell navbar={<Navbar />}>
      <Outlet />
    </AppShell>
  );
}

export default ProtectedRoute;
