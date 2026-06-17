import { Link } from "react-router-dom";

import LogoIcon from "../Logo/LogoIcon";

import Navlinks from "./Navlinks.tsx";

import "./Navbar.css";

function Navbar() {
  return (
    <div className="navbar">
      <Link to="/" className="navbar-brand">
        <LogoIcon className="navbar-logo" />
        Personal Search
      </Link>
      <Navlinks />
    </div>
  );
}

export default Navbar;
