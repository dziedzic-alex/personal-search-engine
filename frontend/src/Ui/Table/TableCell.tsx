import "./TableCell.css";

interface Props {
  children: React.ReactNode;
  sortable?: boolean;
  as?: "th" | "td";
  colSpan?: number;
  onClick?: () => void;
}

function TableCell(props: Props) {
  const { children, as = "td", sortable = false, colSpan = 1, onClick } = props;

  const classNames = [
    "table-cell",
    sortable ? "table-cell-sortable" : undefined,
  ]
    .filter(Boolean)
    .join(" ");

  const Tag = as;

  return (
    <Tag
      className={classNames}
      scope={as === "th" ? "col" : undefined}
      colSpan={colSpan}
      onClick={onClick}
    >
      {children}
    </Tag>
  );
}

export default TableCell;
