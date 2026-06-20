import "./TableBody.css";

interface Props {
  children: React.ReactNode;
}

function TableBody(props: Props) {
  const { children } = props;

  return <tbody className="table-body">{children}</tbody>;
}

export default TableBody;
