"""Provider cost breakdown model."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProviderCostBreakdown(Base):
    """Provider cost breakdown model for tracking costs per provider per request."""

    __tablename__ = "provider_cost_breakdown"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(255), nullable=False)
    subtask_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Relationships
    request: Mapped["Request"] = relationship("Request", back_populates="provider_costs")

    def __repr__(self) -> str:
        return (
            f"<ProviderCostBreakdown(id={self.id}, request_id={self.request_id}, "
            f"provider={self.provider_name}, cost={self.total_cost})>"
        )
