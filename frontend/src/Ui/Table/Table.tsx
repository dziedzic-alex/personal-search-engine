import "./Table.css";

interface Props {
  children: React.ReactNode;
}

function Table(props: Props) {
  const { children } = props;

  return (
    <div className="table-scroll">
      <table className="table-container">{children}</table>
    </div>
  );
}

export default Table;
