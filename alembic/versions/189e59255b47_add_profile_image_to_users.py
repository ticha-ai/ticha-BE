"""Add profile_image to users

Revision ID: 189e59255b47
Revises: b48bccd81211
Create Date: 2025-02-07 17:54:04.144649

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "189e59255b47"
down_revision: Union[str, None] = "b48bccd81211"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("profile_image", sa.String(length=500), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "profile_image")
    # ### end Alembic commands ###
