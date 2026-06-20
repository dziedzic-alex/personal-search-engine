import "./Body.css";

interface Props {
  children: string;
  variant?: "default" | "muted" | "error";
}

function Body(props: Props) {
  const { children, variant = "default" } = props;

  return <p className={`body-${variant}`}>{children}</p>;
}

export default Body;
