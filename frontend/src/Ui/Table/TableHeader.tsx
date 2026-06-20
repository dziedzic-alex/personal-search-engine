import "./TableHeader.css";

interface Props {
  children: React.ReactNode;
}

function TableHeader(props: Props) {
  const { children } = props;

  return <thead className="table-header">{children}</thead>;
}

export default TableHeader;
