import { NavLink } from "react-router-dom";

import "./Navlinks.css";

function Navlinks() {
  return (
    <div className="navlinks">
      <NavLink to="/search">Search</NavLink>
      <NavLink to="/upload">Upload</NavLink>
      <NavLink to="/profile">Profile</NavLink>
    </div>
  );
}

export default Navlinks;
