import "./Header.css";

interface Props {
  children: string;
  level?: 1 | 2 | 3;
}

function Header(props: Props) {
  const { children, level = 1 } = props;

  const Tag = `h${String(level)}` as "h1" | "h2" | "h3";

  return <Tag className={`header-level-${String(level)}`}>{children}</Tag>;
}

export default Header;
