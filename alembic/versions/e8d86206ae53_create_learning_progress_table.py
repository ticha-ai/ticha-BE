"""Create learning_progress table

Revision ID: e8d86206ae53
Revises: bb3a8e9d57db
Create Date: 2025-02-20 01:45:49.551264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8d86206ae53'
down_revision: Union[str, None] = 'bb3a8e9d57db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
