from typing import Annotated

from fastapi import Depends

from shared.s3_client import S3Client, get_s3_client

S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]
