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
  } = props;

  return (
    <input
      type={type}
      className="text-input"
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
      onChange={(event) => {
        onChange(event.target.value);
      }}
    />
  );
}

export default TextInput;
