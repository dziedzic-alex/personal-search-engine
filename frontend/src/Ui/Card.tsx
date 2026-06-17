import "./Card.css";

interface Props {
  children: React.ReactNode;
}

function Card(props: Props) {
  const { children } = props;

  return <div className="card-container">{children}</div>;
}

export default Card;
