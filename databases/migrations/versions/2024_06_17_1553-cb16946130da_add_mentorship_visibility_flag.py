"""Add mentorship visibility flag

Revision ID: cb16946130da
Revises: 4f51a1ae81c0
Create Date: 2024-06-17 15:53:39.789967

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cb16946130da"
down_revision: Union[str, None] = "4f51a1ae81c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "mentorship",
        sa.Column(
            "is_show",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("mentorship", "is_show")
    # ### end Alembic commands ###