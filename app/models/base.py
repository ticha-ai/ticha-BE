from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """기본 Base 클래스"""

    pass


class BaseTimestamp:
    """타임스탬프 믹스인(Mixin)"""

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, onupdate=func.now(), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
