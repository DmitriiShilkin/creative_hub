from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
    Boolean,
    event,
    Connection,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship, Mapper
from sqlalchemy.sql import expression

from models.base import Base
from models.translations import NameTranslations

if TYPE_CHECKING:
    from models.frilance.custom_fields import (
        FileAnswer,
        MultipleChoiceAnswer,
        NumberAnswer,
        SingleChoiceAnswer,
        TextAnswer,
    )
    from models.frilance.job import Job
    from models.media_file import MediaFile
    from models.user import User


class ProposalStatus(NameTranslations):
    __tablename__ = "proposal_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    color: Mapped[str]
    order: Mapped[int] = mapped_column(Integer, server_default="1")
    is_default: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="proposal_statuses"
    )
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal", back_populates="status"
    )


class Proposal(Base):
    __tablename__ = "proposal"
    __table_args__ = (UniqueConstraint("user_id", "job_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, server_default="")
    price: Mapped[Optional[int]]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("job.id", ondelete="CASCADE")
    )
    status_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("proposal_status.id", ondelete="SET NULL")
    )
    is_hidden: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="proposals", foreign_keys=[user_id]
    )
    updated_by: Mapped["User"] = relationship(
        "User",
        back_populates="updated_proposals",
        foreign_keys=[updated_by_id],
    )
    job: Mapped["Job"] = relationship("Job", back_populates="proposals")
    status: Mapped["ProposalStatus"] = relationship(
        "ProposalStatus", back_populates="proposals"
    )
    files: Mapped[list["MediaFile"]] = relationship(
        "MediaFile",
        back_populates="proposal",
    )
    text_answers: Mapped[list["TextAnswer"]] = relationship(
        "TextAnswer",
        back_populates="proposal",
        cascade="all, delete",
        passive_deletes=True,
    )
    single_choice_answers: Mapped[list["SingleChoiceAnswer"]] = relationship(
        "SingleChoiceAnswer",
        back_populates="proposal",
        cascade="all, delete",
        passive_deletes=True,
    )
    number_answers: Mapped[list["NumberAnswer"]] = relationship(
        "NumberAnswer",
        back_populates="proposal",
        cascade="all, delete",
        passive_deletes=True,
    )
    multiple_choice_answers: Mapped[list["MultipleChoiceAnswer"]] = (
        relationship(
            "MultipleChoiceAnswer",
            back_populates="proposal",
            cascade="all, delete",
            passive_deletes=True,
        )
    )
    file_answers: Mapped[list["FileAnswer"]] = relationship(
        "FileAnswer",
        back_populates="proposal",
        cascade="all, delete",
        passive_deletes=True,
    )


def prevent_deletion(
    mapper: Mapper,
    connection: Connection,
    target: ProposalStatus,
) -> None:
    if target.is_default:
        err = "Deleting default status is forbidden"
        raise SQLAlchemyError(err)


event.listen(ProposalStatus, "before_delete", prevent_deletion)
