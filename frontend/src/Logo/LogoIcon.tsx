interface LogoIconProps {
  className?: string;
}

function LogoIcon({ className }: LogoIconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="3 2 26 27"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <rect
        x="4"
        y="3"
        width="12"
        height="16"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="2"
      />
      <line
        x1="7"
        y1="8"
        x2="13"
        y2="8"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="7"
        y1="11.5"
        x2="13"
        y2="11.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="7"
        y1="15"
        x2="11"
        y2="15"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <circle cx="17" cy="17" r="7" stroke="currentColor" strokeWidth="2.25" />
      <path
        d="M22.5 22.5L28 28"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
      />
    </svg>
  );
}

export default LogoIcon;
