import "./Body.css";

interface Props {
  children: React.ReactNode;
  variant?: "default" | "muted" | "error";
  truncate?: boolean;
  tooltip?: string;
}

function Body(props: Props) {
  const {
    children,
    variant = "default",
    truncate = false,
    tooltip = "",
  } = props;

  const classes = [`body-${variant}`, truncate && "body-truncate"]
    .filter(Boolean)
    .join(" ");

  return (
    <p className={classes} title={tooltip || undefined}>
      {children}
    </p>
  );
}

export default Body;
