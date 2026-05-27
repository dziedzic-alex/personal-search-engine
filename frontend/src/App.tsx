import { Routes, Route } from "react-router-dom";

import Navbar from "./Navbar/Navbar.tsx";
import Home from "./Home/Home.tsx";
import Upload from "./Upload/Upload.tsx";
import Search from "./Search/Search.tsx";

import "./App.css";

function App() {
  return (
    <>
      <Navbar />

      <div className="app-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
