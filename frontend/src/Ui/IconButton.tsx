import "./IconButton.css";

interface Props {
  ariaLabel: string;
  children: React.ReactNode;
  onClick: () => void;
  isDisabled?: boolean;
  size?: "small" | "medium";
}

function IconButton(props: Props) {
  const {
    ariaLabel,
    children,
    onClick,
    isDisabled = false,
    size = "medium",
  } = props;

  return (
    <button
      type="button"
      className={`icon-button icon-button-size-${size}`}
      aria-label={ariaLabel}
      onClick={onClick}
      disabled={isDisabled}
    >
      {children}
    </button>
  );
}

export default IconButton;
