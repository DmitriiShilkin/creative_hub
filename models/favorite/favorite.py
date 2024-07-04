from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models import Event, Job, Organisation
    from models.user import User


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    favorite_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    organisation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organisation.id", ondelete="CASCADE"),
        nullable=True,
    )
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        nullable=True,
    )
    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job.id", ondelete="CASCADE"),
        nullable=True,
    )
    organization: Mapped["Organisation"] = relationship(
        "Organisation",
        back_populates="favorites",
    )
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="favorites",
    )
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="favorites",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="favorites",
        foreign_keys=[user_id],
    )
