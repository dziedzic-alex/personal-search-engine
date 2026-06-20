import "./TableRow.css";

interface Props {
  children: React.ReactNode;
}

function TableRow(props: Props) {
  const { children } = props;

  return <tr className="table-row">{children}</tr>;
}

export default TableRow;
