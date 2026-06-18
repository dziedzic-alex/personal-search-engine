import "./Stack.css";

interface Props {
  children: React.ReactNode;
  direction?: "vertical" | "horizontal";
  spacing?: "sm" | "md" | "lg";
  align?: "start" | "center" | "end" | "stretch";
  className?: string;
}

function Stack(props: Props) {
  const {
    children,
    direction = "vertical",
    spacing = "md",
    align,
    className,
  } = props;

  const classes = [
    "stack",
    `stack-${direction}`,
    `stack-spacing-${spacing}`,
    align ? `stack-align-${align}` : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <div className={classes}>{children}</div>;
}

export default Stack;
