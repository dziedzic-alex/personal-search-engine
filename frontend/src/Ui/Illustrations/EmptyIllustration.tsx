interface Props {
  className?: string;
}

function EmptyIllustration(props: Props) {
  const { className } = props;

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <rect
        x="10"
        y="14"
        width="44"
        height="36"
        rx="3"
        stroke="currentColor"
        strokeWidth="2"
      />
      <path
        d="M10 24h44"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M18 34h20M18 40h28M18 46h14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.45"
      />
    </svg>
  );
}

export default EmptyIllustration;
