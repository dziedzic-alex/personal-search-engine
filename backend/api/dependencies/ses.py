from typing import Annotated
from fastapi import Depends
from shared.ses_client import SESClient, get_ses_client

SESClientDep = Annotated[SESClient, Depends(get_ses_client)]