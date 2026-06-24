import "./TextInput.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
  type?: "text" | "email" | "password" | "search";
  name?: string;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  id?: string;
  isDisabled?: boolean;
  autoFocus?: boolean;
  onEnter?: () => void;
  className?: string;
  inputMode?: React.HTMLAttributes<HTMLInputElement>["inputMode"];
  enterKeyHint?: React.HTMLAttributes<HTMLInputElement>["enterKeyHint"];
}

function TextInput(props: Props) {
  const {
    value,
    onChange,
    type = "text",
    name,
    placeholder,
    autoComplete,
    required,
    minLength,
    maxLength,
    id,
    isDisabled = false,
    autoFocus,
    onEnter,
    className,
    inputMode,
    enterKeyHint,
  } = props;

  const classes = ["text-input", className].filter(Boolean).join(" ");

  return (
    <input
      type={type}
      className={classes}
      value={value}
      name={name}
      placeholder={placeholder}
      autoComplete={autoComplete}
      required={required}
      minLength={minLength}
      maxLength={maxLength}
      id={id}
      disabled={isDisabled}
      autoFocus={autoFocus}
      inputMode={inputMode}
      enterKeyHint={enterKeyHint}
      onKeyDown={(event) => {
        if (event.key === "Enter" && onEnter && !isDisabled) {
          event.preventDefault();
          onEnter();
        }
      }}
      onChange={(event) => {
        onChange(event.target.value);
      }}
    />
  );
}

export default TextInput;
