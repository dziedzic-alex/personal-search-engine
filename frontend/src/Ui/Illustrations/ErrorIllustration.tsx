interface Props {
  className?: string;
}

function ErrorIllustration(props: Props) {
  const { className } = props;

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <circle cx="32" cy="32" r="24" stroke="currentColor" strokeWidth="2" />
      <path
        d="M32 20v18"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx="32" cy="44" r="1.75" fill="currentColor" />
    </svg>
  );
}

export default ErrorIllustration;
