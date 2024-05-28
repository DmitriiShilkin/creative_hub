"""Add calendar

Revision ID: a9bd3a73fcb9
Revises: 7805ffc02710
Create Date: 2024-05-27 10:46:15.571918

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a9bd3a73fcb9"
down_revision: Union[str, None] = "7805ffc02710"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum(
        "EVERY_DAY",
        "EVERY_WEEK",
        "EVERY_MONTH",
        "NO_REPEATS",
        name="calendareventrepeatability",
    ).create(op.get_bind())
    sa.Enum(
        "IMPORTANT",
        "REQUIRES_ATTENTION",
        "WITHOUT_PRIORITY",
        name="calendareventpriority",
    ).create(op.get_bind())
    sa.Enum(
        "MEETING",
        "IMPORTANT_DATE",
        "PERSONAL",
        "NO_CATEGORY",
        name="calendareventtype",
    ).create(op.get_bind())
    op.create_table(
        "calendar_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "event_type",
            postgresql.ENUM(
                "MEETING",
                "IMPORTANT_DATE",
                "PERSONAL",
                "NO_CATEGORY",
                name="calendareventtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            postgresql.ENUM(
                "IMPORTANT",
                "REQUIRES_ATTENTION",
                "WITHOUT_PRIORITY",
                name="calendareventpriority",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "repeatability",
            postgresql.ENUM(
                "EVERY_DAY",
                "EVERY_WEEK",
                "EVERY_MONTH",
                "NO_REPEATS",
                name="calendareventrepeatability",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("organizer_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organizer_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calendar_event_id"), "calendar_event", ["id"], unique=False
    )
    op.create_table(
        "calendar_event_comment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["calendar_event.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calendar_event_comment_id"),
        "calendar_event_comment",
        ["id"],
        unique=False,
    )
    op.create_table(
        "calendar_event_users",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"], ["calendar_event.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id", "user_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("calendar_event_users")
    op.drop_index(
        op.f("ix_calendar_event_comment_id"),
        table_name="calendar_event_comment",
    )
    op.drop_table("calendar_event_comment")
    op.drop_index(op.f("ix_calendar_event_id"), table_name="calendar_event")
    op.drop_table("calendar_event")
    sa.Enum(
        "MEETING",
        "IMPORTANT_DATE",
        "PERSONAL",
        "NO_CATEGORY",
        name="calendareventtype",
    ).drop(op.get_bind())
    sa.Enum(
        "IMPORTANT",
        "REQUIRES_ATTENTION",
        "WITHOUT_PRIORITY",
        name="calendareventpriority",
    ).drop(op.get_bind())
    sa.Enum(
        "EVERY_DAY",
        "EVERY_WEEK",
        "EVERY_MONTH",
        "NO_REPEATS",
        name="calendareventrepeatability",
    ).drop(op.get_bind())
    # ### end Alembic commands ###