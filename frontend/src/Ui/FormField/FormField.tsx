import TextInput from "../TextInput/TextInput.tsx";

import type { ReactElement } from "react";

import "./FormField.css";

interface Props {
  label: string;
  children: ReactElement<React.ComponentProps<typeof TextInput>>;
}

function FormField(props: Props) {
  const { label, children } = props;

  return (
    <label className="form-field">
      <span className="form-field-label">{label}</span>
      {children}
    </label>
  );
}

export default FormField;
