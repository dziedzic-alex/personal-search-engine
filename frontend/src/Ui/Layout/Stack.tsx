import "./Stack.css";

interface Props {
  children: React.ReactNode;
  direction?: "vertical" | "horizontal";
  spacing?: "xs" | "sm" | "md" | "lg";
  justify?: "start" | "center" | "end";
  align?: "start" | "center" | "end" | "stretch";
  className?: string;
}

function Stack(props: Props) {
  const {
    children,
    direction = "vertical",
    spacing = "md",
    justify,
    align,
    className,
  } = props;

  const classes = [
    "stack",
    `stack-${direction}`,
    `stack-spacing-${spacing}`,
    justify ? `stack-justify-${justify}` : "",
    align ? `stack-align-${align}` : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <div className={classes}>{children}</div>;
}

export default Stack;
