import Button from "../Buttons/Button";
import CenteredPanel from "../Layout/CenteredPanel";
import Stack from "../Layout/Stack";
import Body from "../Typography/Body";
import Header from "../Typography/Header";

import "./StatePanel.css";

interface Props {
  illustration: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  fullHeight?: boolean;
}

function StatePanel(props: Props) {
  const {
    illustration,
    title,
    description,
    action,
    fullHeight = false,
  } = props;

  return (
    <CenteredPanel fullHeight={fullHeight}>
      <Stack spacing="md" align="center" className="state-panel-content">
        <div className="state-panel-illustration">{illustration}</div>
        <Header level={2}>{title}</Header>
        {description ? <Body variant="muted">{description}</Body> : null}
        {action ? (
          <Button onClick={action.onClick}>{action.label}</Button>
        ) : null}
      </Stack>
    </CenteredPanel>
  );
}

export default StatePanel;
