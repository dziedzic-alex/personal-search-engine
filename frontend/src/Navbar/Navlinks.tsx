import { NavLink } from "react-router-dom";

import "./Navlinks.css";

function Navlinks() {
  return (
    <div className="navlinks">
      <NavLink to="/search">Search</NavLink>
      <NavLink to="/files">Files</NavLink>
      <NavLink to="/account">Account</NavLink>
    </div>
  );
}

export default Navlinks;
