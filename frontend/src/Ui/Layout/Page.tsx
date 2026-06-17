import "./Page.css";

interface Props {
  children: React.ReactNode;
}

function Page(props: Props) {
  const { children } = props;

  return <div className="page-container">{children}</div>;
}

export default Page;
