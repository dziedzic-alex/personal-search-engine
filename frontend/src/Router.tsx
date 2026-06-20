import { createBrowserRouter, Outlet } from "react-router-dom";

import AuthProvider from "./Auth/AuthProvider.tsx";
import Login from "./Auth/Login.tsx";
import Signup from "./Auth/Signup.tsx";
import Files from "./Files/Files.tsx";
import Home from "./Home/Home.tsx";
import Profile from "./Profile/Profile.tsx";
import ProtectedRoute from "./ProtectedRoute.tsx";
import Search from "./Search/Search.tsx";
import NotificationProvider from "./Ui/Notification/NotificationProvider.tsx";

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
      { path: "/login", element: <Login /> },
      { path: "/signup", element: <Signup /> },
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
