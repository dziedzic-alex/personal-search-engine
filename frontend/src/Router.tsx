import { createBrowserRouter, Outlet } from "react-router-dom";

import AuthProvider from "./Auth/AuthProvider.tsx";
import Login from "./Auth/Login.tsx";
import Signup from "./Auth/Signup.tsx";
import Home from "./Home/Home.tsx";
import Profile from "./Profile/Profile.tsx";
import ProtectedRoute from "./ProtectedRoute.tsx";
import Search from "./Search/Search.tsx";
import Upload from "./Upload/Upload.tsx";

const router = createBrowserRouter([
  {
    element: (
      <AuthProvider>
        <Outlet />
      </AuthProvider>
    ),
    children: [
      { path: "/login", element: <Login /> },
      { path: "/signup", element: <Signup /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/", element: <Home /> },
          { path: "/upload", element: <Upload /> },
          { path: "/search", element: <Search /> },
          { path: "/profile", element: <Profile /> },
        ],
      },
    ],
  },
]);

export { router };
