import CenteredPanel from "../Layout/CenteredPanel";
import Spinner from "../Spinner/Spinner";

function LoadingPage() {
  return (
    <CenteredPanel fullHeight>
      <Spinner size="large" />
    </CenteredPanel>
  );
}

export default LoadingPage;
