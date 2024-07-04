"""add job favorites

Revision ID: 4f0c2a49e024
Revises: 658a9c52e32d
Create Date: 2024-07-04 12:00:03.840134

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4f0c2a49e024"
down_revision: Union[str, None] = "658a9c52e32d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "favorites", sa.Column("job_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "favorites_job_id_fkey",
        "favorites",
        "job",
        ["job_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "favorites_job_id_fkey", "favorites", type_="foreignkey"
    )
    op.drop_column("favorites", "job_id")
    # ### end Alembic commands ###
