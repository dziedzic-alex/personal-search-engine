import "./CenteredPanel.css";

interface Props {
  children: React.ReactNode;
  fullHeight?: boolean;
}

function CenteredPanel(props: Props) {
  const { children, fullHeight = false } = props;

  const className = [
    "centered-panel",
    fullHeight ? "centered-panel-full-height" : "centered-panel-inline",
  ].join(" ");

  return <div className={className}>{children}</div>;
}

export default CenteredPanel;
