import "./Badge.css";

interface Props {
  children: React.ReactNode;
  level: "neutral" | "info" | "success" | "danger";
}

function Badge(props: Props) {
  const { children, level } = props;

  return <span className={`badge badge-${level}`}>{children}</span>;
}

export default Badge;
