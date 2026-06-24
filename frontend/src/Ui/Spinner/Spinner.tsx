import "./Spinner.css";

interface Props {
  size?: "small" | "medium" | "large";
  ariaHidden?: boolean;
}

function Spinner(props: Props) {
  const { size = "medium", ariaHidden = false } = props;

  return (
    <span
      className={`spinner-size-${size}`}
      aria-hidden={ariaHidden || undefined}
      {...(!ariaHidden && { role: "status", "aria-label": "Loading" })}
    />
  );
}

export default Spinner;
