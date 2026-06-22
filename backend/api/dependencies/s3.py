from typing import Annotated

from fastapi import Depends
from shared.s3_client import get_s3_client, S3Client

S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]