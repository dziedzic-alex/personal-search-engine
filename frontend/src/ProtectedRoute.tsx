import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "./Auth/AuthContext.tsx";
import Navbar from "./Navbar/Navbar.tsx";
import LoadingPage from "./Ui/LoadingPage/LoadingPage.tsx";

function ProtectedRoute() {
  const { user, isRefreshingAccessToken } = useAuth();

  if (!user && isRefreshingAccessToken) {
    return <LoadingPage />;
  } else if (!user && !isRefreshingAccessToken) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Navbar />
      <div className="app-content">
        <Outlet />
      </div>
    </>
  );
}

export default ProtectedRoute;
