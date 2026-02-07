"""Request model."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Request(Base):
    """Request model for user queries."""

    __tablename__ = "requests"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="requests")
    response: Mapped[Optional["Response"]] = relationship(
        "Response", back_populates="request", cascade="all, delete-orphan", uselist=False
    )
    subtasks: Mapped[List["Subtask"]] = relationship(
        "Subtask", back_populates="request", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, user_id={self.user_id}, status={self.status})>"
