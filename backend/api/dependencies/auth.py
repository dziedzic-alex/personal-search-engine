from typing import Annotated

from fastapi import Depends

from api.routers.auth.auth_utils import get_current_user
from db.models.user import User

UserDep = Annotated[User, Depends(get_current_user)]
