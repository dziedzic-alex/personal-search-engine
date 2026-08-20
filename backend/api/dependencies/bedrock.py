from typing import Annotated

from fastapi import Depends

from shared.bedrock_client import BedrockClient, get_bedrock_client

BedrockClientDep = Annotated[BedrockClient, Depends(get_bedrock_client)]
