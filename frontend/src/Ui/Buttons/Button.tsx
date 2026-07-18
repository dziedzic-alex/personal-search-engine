import Spinner from "../Spinner/Spinner";

import "./Button.css";

interface Props {
  children: string;
  type?: "button" | "submit";
  variant?: "primary" | "secondary" | "danger";
  onClick?: () => void;
  isDisabled?: boolean;
  isLoading?: boolean;
  loadingText?: string;
  size?: "small" | "medium" | "large";
  fullWidth?: boolean;
}

function Button(props: Props) {
  const {
    children,
    type = "button",
    variant = "primary",
    onClick,
    isDisabled = false,
    isLoading = false,
    loadingText,
    size = "medium",
    fullWidth = false,
  } = props;

  const classNames = [
    `button-${variant}`,
    `button-size-${size}`,
    fullWidth && "button-full-width",
  ]
    .filter(Boolean)
    .join(" ");

  let buttonContent: React.ReactNode = children;

  if (isLoading) {
    buttonContent = (
      <>
        <Spinner size="small" ariaHidden={loadingText ? true : false} />
        {loadingText}
      </>
    );
  }

  return (
    <button
      type={type}
      className={classNames}
      onClick={onClick}
      disabled={isDisabled || isLoading}
      aria-busy={isLoading}
    >
      {buttonContent}
    </button>
  );
}

export default Button;
