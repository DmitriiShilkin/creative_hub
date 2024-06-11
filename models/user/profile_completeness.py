from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from .user import User


class ProfileCompleteness(Base):
    """
    Модель процента заполненности профиля пользователя

    # Attrs:
        - id: int
        - main_percentage: int - Общий процент по профилю
        - contacts_percentage: int - Процент заполненности Contact info
        - experience_percentage: int - Процент заполненности Experience
        - education_percentage: int - Процент заполненности Education
        - mentorship_percentage: int - Процент заполненности Mentorship
        - user_id: int (FK) - Идентификатор пользователя
        - user: User - Модель пользователя.
    """

    __tablename__ = "user_profile_completeness"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    main_percentage: Mapped[int] = mapped_column(Integer, server_default="0")
    contacts_percentage: Mapped[int] = mapped_column(
        Integer, server_default="0"
    )
    education_percentage: Mapped[int] = mapped_column(
        Integer, server_default="0"
    )
    experience_percentage: Mapped[int] = mapped_column(
        Integer, server_default="0"
    )
    mentorship_percentage: Mapped[int] = mapped_column(
        Integer, server_default="0"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="profile_completeness"
    )

    def __repr__(self) -> str:
        return f"Main percentage {self.main_percentage}"
