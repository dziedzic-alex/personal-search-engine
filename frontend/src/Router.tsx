import { createBrowserRouter, Outlet } from "react-router-dom";

import AuthProvider from "./Auth/AuthProvider";
import Login from "./Auth/Login";
import Signup from "./Auth/Signup";
import AuthLayout from "./AuthLayout";
import Files from "./Files/Files";
import Home from "./Home/Home";
import Profile from "./Profile/Profile";
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
        ],
      },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/", element: <Home /> },
          { path: "/files", element: <Files /> },
          { path: "/search", element: <Search /> },
          { path: "/profile", element: <Profile /> },
        ],
      },
    ],
  },
]);

export { router };
