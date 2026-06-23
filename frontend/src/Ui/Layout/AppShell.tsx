import Page from "./Page.tsx";

import "./AppShell.css";

interface Props {
  children: React.ReactNode;
  navbar?: React.ReactNode;
}

function AppShell(props: Props) {
  const { children, navbar } = props;

  return (
    <div className="app-shell">
      {navbar}
      <Page>{children}</Page>
    </div>
  );
}

export default AppShell;
