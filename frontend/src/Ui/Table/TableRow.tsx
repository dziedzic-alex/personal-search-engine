import "./TableRow.css";

interface Props {
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  onDoubleClick?: () => void;
  isSelected?: boolean;
}

function TableRow(props: Props) {
  const { children, onClick, onDoubleClick, isSelected } = props;

  const classNames = [
    "table-row",
    isSelected ? "table-row-selected" : "",
    onClick ? "table-row-clickable" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <tr className={classNames} onClick={onClick} onDoubleClick={onDoubleClick}>
      {children}
    </tr>
  );
}

export default TableRow;
