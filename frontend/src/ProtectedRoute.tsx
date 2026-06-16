import { Navigate, Outlet } from "react-router-dom";

import Navbar from "./Navbar/Navbar.tsx";
import { useAuth } from "./Auth/AuthContext.tsx";

function ProtectedRoute() {
  const { user, isRefreshingAccessToken } = useAuth();

  if (!user && isRefreshingAccessToken) {
    return <div>Loading...</div>;
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
