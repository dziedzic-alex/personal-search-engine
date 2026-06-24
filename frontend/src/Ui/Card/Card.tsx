import "./Card.css";

interface Props {
  children: React.ReactNode;
  className?: string;
}

function Card(props: Props) {
  const { children, className } = props;

  const classes = ["card-container", className].filter(Boolean).join(" ");

  return <div className={classes}>{children}</div>;
}

export default Card;
