import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { use } from "react";

import Navbar from "./Navbar/Navbar.tsx";
import Home from "./Home/Home.tsx";
import Upload from "./Upload/Upload.tsx";
import Search from "./Search/Search.tsx";

import "./App.css";
import { AuthContext } from "./Auth/AuthContext.tsx";
import Login from "./Auth/Login.tsx";
import Signup from "./Auth/Signup.tsx";

function ProtectedRoute() {
  const { user } = use(AuthContext);
  if (!user) {
    return <Navigate to="/login" />;
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

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/search" element={<Search />} />
      </Route>
    </Routes>
  );
}

export default App;
