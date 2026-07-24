import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class UserPlan(enum.StrEnum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ULTRA = "ultra"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(String(255))
    plan: Mapped[UserPlan] = mapped_column(
        Enum(
            UserPlan,
            name="plan_type",
            values_callable=lambda enum_members: [
                enum_member.value for enum_member in enum_members
            ],
        ),
        insert_default=UserPlan.FREE,
    )
    created_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=datetime.now
    )
