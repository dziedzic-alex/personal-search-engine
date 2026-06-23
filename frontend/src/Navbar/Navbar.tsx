import { Link } from "react-router-dom";

import LogoIcon from "../Logo/LogoIcon";

import Navlinks from "./Navlinks.tsx";

import "./Navbar.css";

interface Props {
  variant?: "authed" | "notauthed";
}

function Navbar(props: Props) {
  const { variant = "authed" } = props;

  if (variant === "notauthed") {
    return (
      <div className="navbar">
        <div className="navbar-brand">
          <LogoIcon className="navbar-logo" />
          Personal Search
        </div>
      </div>
    );
  }

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
