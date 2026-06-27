import "./Stack.css";

interface Props {
  children: React.ReactNode;
  direction?: "vertical" | "horizontal";
  spacing?: "xs" | "sm" | "md" | "lg";
  justify?: "start" | "center" | "end";
  align?: "start" | "center" | "end" | "stretch";
  className?: string;
  fullWidth?: boolean;
}

function Stack(props: Props) {
  const {
    children,
    direction = "vertical",
    spacing = "md",
    justify,
    align,
    className,
    fullWidth = false,
  } = props;

  const classes = [
    "stack",
    `stack-${direction}`,
    `stack-spacing-${spacing}`,
    justify ? `stack-justify-${justify}` : "",
    align ? `stack-align-${align}` : "",
    fullWidth ? `stack-full-width` : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <div className={classes}>{children}</div>;
}

export default Stack;
