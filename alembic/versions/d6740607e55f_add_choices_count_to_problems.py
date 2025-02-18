"""add_choices_count_to_problems

Revision ID: d6740607e55f
Revises: 189e59255b47
Create Date: 2025-02-19 02:42:18.773123

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6740607e55f"
down_revision: Union[str, None] = "189e59255b47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("problems", sa.Column("choices_count", sa.Integer(), nullable=False))
    op.drop_index("google_id", table_name="users")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "google_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("google_id", mysql.VARCHAR(length=255), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "auth_provider",
            mysql.VARCHAR(length=50),
            server_default=sa.text("'local'"),
            nullable=False,
        ),
    )
    op.create_index("google_id", "users", ["google_id"], unique=True)
    op.drop_column("problems", "choices_count")
    # ### end Alembic commands ###
