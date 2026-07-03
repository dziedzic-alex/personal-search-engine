import "./Table.css";

interface Props {
  children: React.ReactNode;
  onScroll?: (event: React.UIEvent<HTMLDivElement>) => void;
}

function Table(props: Props) {
  const { children, onScroll } = props;

  return (
    <div onScroll={onScroll} className="table-scroll">
      <table className="table-container">{children}</table>
    </div>
  );
}

export default Table;
