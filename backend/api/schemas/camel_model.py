from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# Pydantic model that converts camelCase to snake_case on incoming requests
# and snake_case to camelCase on outgoing responses
class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )
