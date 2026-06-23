import Spinner from "./Spinner";

import "./Button.css";

interface Props {
  children: string;
  type?: "button" | "submit";
  variant?: "primary" | "secondary";
  onClick?: () => void;
  isDisabled?: boolean;
  isLoading?: boolean;
  loadingText?: string;
  size?: "small" | "medium" | "large";
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
  } = props;

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
      className={`button-${variant} button-size-${size}`}
      onClick={onClick}
      disabled={isDisabled || isLoading}
      aria-busy={isLoading}
    >
      {buttonContent}
    </button>
  );
}

export default Button;
