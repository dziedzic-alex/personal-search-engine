import "./IconButton.css";

interface Props {
  ariaLabel: string;
  children: React.ReactNode;
  onClick: () => void;
  isDisabled?: boolean;
  size?: "small" | "medium" | "large";
  className?: string;
}

function IconButton(props: Props) {
  const {
    ariaLabel,
    children,
    onClick,
    isDisabled = false,
    size = "medium",
    className,
  } = props;

  const classes = ["icon-button", `icon-button-size-${size}`, className]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      type="button"
      className={classes}
      aria-label={ariaLabel}
      onClick={onClick}
      disabled={isDisabled}
    >
      {children}
    </button>
  );
}

export default IconButton;
