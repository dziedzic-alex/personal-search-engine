import { createBrowserRouter, Outlet } from "react-router-dom";

import Account from "./Account/Account";
import AuthProvider from "./Auth/AuthProvider";
import Login from "./Auth/Login";
import Signup from "./Auth/Signup";
import ConfirmEmail from "./Auth/ConfirmEmail";
import PendingEmailVerification from "./Auth/PendingEmailVerification";
import AuthLayout from "./AuthLayout";
import Files from "./Files/Files";
import Home from "./Home/Home";
import ProtectedRoute from "./ProtectedRoute";
import Search from "./Search/Search";
import NotificationProvider from "./Ui/Notification/NotificationProvider";

const router = createBrowserRouter([
  {
    element: (
      <NotificationProvider>
        <AuthProvider>
          <Outlet />
        </AuthProvider>
      </NotificationProvider>
    ),
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: "/login", element: <Login /> },
          { path: "/signup", element: <Signup /> },
          { path: "/verify-email", element: <PendingEmailVerification /> },
          { path: "/verify-email/confirm", element: <ConfirmEmail /> },
        ],
      },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/", element: <Home /> },
          { path: "/files", element: <Files /> },
          { path: "/search", element: <Search /> },
          { path: "/account", element: <Account /> },
        ],
      },
    ],
  },
]);

export { router };
