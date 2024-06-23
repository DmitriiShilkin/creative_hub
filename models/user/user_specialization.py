import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from constants.finance import Currency, PaymentPer
from constants.user_specialization import Grade, Status
from models.base import Base
from models.m2m import UserSpecializationKeywords, UsersSpecializations
from utilities.i18n import CustomTranslatableMixin

if TYPE_CHECKING:
    from models.keyword import Keyword

    from .specialization import Specialization
    from .user import User


class UserSpecialization(Base, CustomTranslatableMixin):
    __tablename__ = "user_specialization"

    translation_fields = dict(description=mapped_column(String))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uid: Mapped[uuid.UUID] = mapped_column(
        UUID, unique=True, index=True, default=uuid.uuid4
    )
    grade: Mapped[Optional[Grade]] = mapped_column(
        ENUM(Grade, create_type=False)
    )
    status: Mapped[Optional[Status]] = mapped_column(
        ENUM(Status, create_type=False)
    )
    price: Mapped[Optional[int]]
    currency: Mapped[Optional[Currency]] = mapped_column(
        ENUM(Currency, create_type=False)
    )
    payment_per: Mapped[Optional[PaymentPer]] = mapped_column(
        ENUM(PaymentPer, create_type=False)
    )
    is_ready_to_move: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    is_ready_for_remote_work: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="specialization", single_parent=True
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        "Keyword",
        back_populates="user_specializations",
        secondary=UserSpecializationKeywords.__table__,
    )
    specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        back_populates="users_specialization",
        secondary=UsersSpecializations.__table__,
    )

    def __str__(self) -> str:
        return f"{self.id}"
