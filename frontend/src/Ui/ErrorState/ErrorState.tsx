import ErrorIllustration from "../Illustrations/ErrorIllustration";
import StatePanel from "../StatePanel/StatePanel";

interface Props {
  title?: string;
  description: string;
  illustration?: React.ReactNode;
  onRetry?: () => void;
  fullHeight?: boolean;
}

function ErrorState(props: Props) {
  const {
    title = "Something went wrong",
    description,
    illustration = <ErrorIllustration />,
    onRetry,
    fullHeight = false,
  } = props;

  return (
    <StatePanel
      illustration={illustration}
      title={title}
      description={description}
      action={
        onRetry
          ? {
              label: "Try again",
              onClick: onRetry,
            }
          : undefined
      }
      fullHeight={fullHeight}
    />
  );
}

export default ErrorState;
