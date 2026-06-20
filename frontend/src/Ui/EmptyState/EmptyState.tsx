import EmptyIllustration from "../Illustrations/EmptyIllustration";
import StatePanel from "../StatePanel/StatePanel";

interface Props {
  title: string;
  description?: string;
  illustration?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  fullHeight?: boolean;
}

function EmptyState(props: Props) {
  const {
    title,
    description,
    illustration = <EmptyIllustration />,
    action,
    fullHeight = false,
  } = props;

  return (
    <StatePanel
      illustration={illustration}
      title={title}
      description={description}
      action={action}
      fullHeight={fullHeight}
    />
  );
}

export default EmptyState;
