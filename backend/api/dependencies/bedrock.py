from typing import Annotated
from shared.bedrock_client import BedrockClient, get_bedrock_client
from fastapi import Depends

BedrockClientDep = Annotated[BedrockClient, Depends(get_bedrock_client)]