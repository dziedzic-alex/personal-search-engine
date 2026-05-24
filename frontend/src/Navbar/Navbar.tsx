import { Link } from "react-router-dom";

import Navlinks from "./Navlinks.tsx";

import "./Navbar.css";

function Navbar() {
  return (
    <div className="navbar">
      <Link to="/"> Personal Search Engine 🔎</Link>
      <Navlinks />
    </div>
  );
}

export default Navbar;
