from sqlalchemy import Column, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase


# Base 클래스 정의
class Base(DeclarativeBase):
    pass


class BaseTimestamp:
    created_at = Column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )  # 생성 시간
    updated_at = Column(TIMESTAMP, onupdate=func.now())  # 수정 시간
    deleted_at = Column(TIMESTAMP, nullable=True)  # 삭제 시간 (soft delete)
