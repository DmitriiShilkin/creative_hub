from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from constants.finance import Currency, PaymentPer
from constants.user_specialization import Grade
from models.base import Base
from models.m2m import (
    MentorshipDemands,
    MentorshipKeywords,
    MentorshipSpecializations,
)
from utilities.i18n import CustomTranslatableMixin

if TYPE_CHECKING:
    from models.keyword import Keyword

    from .specialization import Specialization
    from .user import User


class MentorshipDemand(Base):
    __tablename__ = "mentorship_demand"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str]
    mentorship: Mapped[list["Mentorship"]] = relationship(
        "Mentorship",
        back_populates="demands",
        secondary=MentorshipDemands.__table__,
    )


class Mentorship(Base, CustomTranslatableMixin):
    """
    Модель наставничества.

    # Attrs:
        - id: int
        - grade: Grade - Уровень навыков.
        - is_paid: bool - Оплачено или нет.
        - price: int - Цена.
        - first_is_free: bool - Сначала бесплатно или нет.
        - currency: Currency - Валюта для оплаты (из констант).
        - payment_per: PaymentPer - За какой период оплата (из констант).
        - user_id: int (FK) - Идентификатор пользователя.
        - user: User - Пользователи связанные с наставничеством.
        - demands: list[Keyword] - Требования для наставничества.
        - keywords: list[Keyword] - Ключевые навыки/слова.
        - specializations: List[Specialization] - Специализации.
    """

    __tablename__ = "mentorship"

    translation_fields = dict(description=mapped_column(String))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grades: Mapped[Optional[list[Grade]]] = mapped_column(
        ARRAY(ENUM(Grade, create_type=False))
    )

    is_show: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.true()
    )
    is_paid: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    price: Mapped[Optional[int]]
    first_is_free: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    currency: Mapped[Optional[Currency]] = mapped_column(
        ENUM(Currency, create_type=False)
    )
    payment_per: Mapped[Optional[PaymentPer]] = mapped_column(
        ENUM(PaymentPer, create_type=False)
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship("User", back_populates="mentorship")
    demands: Mapped[list["MentorshipDemand"]] = relationship(
        "MentorshipDemand",
        back_populates="mentorship",
        secondary=MentorshipDemands.__table__,
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        "Keyword",
        back_populates="mentorship",
        secondary=MentorshipKeywords.__table__,
    )
    specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        back_populates="mentorship",
        secondary=MentorshipSpecializations.__table__,
    )
