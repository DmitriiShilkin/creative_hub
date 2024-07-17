from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.frilance.job import Job
    from models.user import User


class JobView(Base):
    __tablename__ = "job_view"
    __table_args__ = (UniqueConstraint("user_id", "job_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip_address: Mapped[Optional[str]]
    proposals_views: Mapped[int]
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("job.id", ondelete="CASCADE")
    )
    job: Mapped["Job"] = relationship("Job", back_populates="job_views")
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="job_views"
    )
