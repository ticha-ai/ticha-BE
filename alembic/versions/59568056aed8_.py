"""empty message

Revision ID: 59568056aed8
Revises: c3630e9eb4e0, 15452612bba7
Create Date: 2025-01-28 01:27:07.680898

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59568056aed8"
down_revision: Union[str, None] = ("c3630e9eb4e0", "15452612bba7")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
