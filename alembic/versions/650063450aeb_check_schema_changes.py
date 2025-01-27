"""check schema changes

Revision ID: 650063450aeb
Revises: 9c50b61c0cb2
Create Date: 2025-01-24 00:44:33.307488

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "650063450aeb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "answer_sheets",
        "unanswered_count",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "chapters", "problems_count", existing_type=mysql.INTEGER(), nullable=False
    )
    op.alter_column(
        "problems", "attempt_count", existing_type=mysql.INTEGER(), nullable=False
    )
    op.alter_column(
        "problems", "correct_count", existing_type=mysql.INTEGER(), nullable=False
    )
    op.alter_column(
        "study_logs", "quiz_count", existing_type=mysql.INTEGER(), nullable=False
    )
    op.alter_column(
        "user_answers",
        "is_correct",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )
    op.alter_column(
        "user_answers",
        "is_starred",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )
    op.alter_column(
        "user_answers",
        "has_answer",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )
    op.alter_column(
        "user_problems_stat",
        "is_starred",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )
    op.alter_column(
        "user_problems_stat",
        "correct_attempts_count",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "user_problems_stat",
        "total_attempts_count",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "users",
        "review_completed_quizzes_count",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "users", "graded_quizzes_count", existing_type=mysql.INTEGER(), nullable=False
    )
    op.alter_column(
        "users", "ongoing_quizzes_count", existing_type=mysql.INTEGER(), nullable=False
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )
    op.alter_column(
        "users",
        "is_deleted",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users",
        "is_deleted",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True,
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True,
    )
    op.alter_column(
        "users", "ongoing_quizzes_count", existing_type=mysql.INTEGER(), nullable=True
    )
    op.alter_column(
        "users", "graded_quizzes_count", existing_type=mysql.INTEGER(), nullable=True
    )
    op.alter_column(
        "users",
        "review_completed_quizzes_count",
        existing_type=mysql.INTEGER(),
        nullable=True,
    )
    op.alter_column(
        "user_problems_stat",
        "total_attempts_count",
        existing_type=mysql.INTEGER(),
        nullable=True,
    )
    op.alter_column(
        "user_problems_stat",
        "correct_attempts_count",
        existing_type=mysql.INTEGER(),
        nullable=True,
    )
    op.alter_column(
        "user_problems_stat",
        "is_starred",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True,
    )
    op.alter_column(
        "user_answers",
        "has_answer",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True,
    )
    op.alter_column(
        "user_answers",
        "is_starred",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True,
    )
    op.alter_column(
        "user_answers",
        "is_correct",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True,
    )
    op.alter_column(
        "study_logs", "quiz_count", existing_type=mysql.INTEGER(), nullable=True
    )
    op.alter_column(
        "problems", "correct_count", existing_type=mysql.INTEGER(), nullable=True
    )
    op.alter_column(
        "problems", "attempt_count", existing_type=mysql.INTEGER(), nullable=True
    )
    op.alter_column(
        "chapters", "problems_count", existing_type=mysql.INTEGER(), nullable=True
    )
    op.alter_column(
        "answer_sheets",
        "unanswered_count",
        existing_type=mysql.INTEGER(),
        nullable=True,
    )
    # ### end Alembic commands ###
