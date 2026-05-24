import { Link } from "react-router-dom";

import "./Navlinks.css";

function Navlinks() {
  return (
    <div className="navlinks">
      <Link to="/upload"> Upload </Link>
    </div>
  );
}

export default Navlinks;
