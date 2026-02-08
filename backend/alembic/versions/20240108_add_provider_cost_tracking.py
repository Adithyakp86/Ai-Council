"""Add provider cost tracking

Revision ID: 20240108_0001
Revises: 20240101_0000
Create Date: 2024-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240108_0001'
down_revision = '20240101_0000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add provider_cost_breakdown table for tracking costs per provider."""
    op.create_table(
        'provider_cost_breakdown',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('requests.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('provider_name', sa.String(100), nullable=False, index=True),
        sa.Column('model_id', sa.String(255), nullable=False),
        sa.Column('subtask_count', sa.Integer, nullable=False, default=0),
        sa.Column('total_cost', sa.Float, nullable=False, default=0.0),
        sa.Column('total_input_tokens', sa.Integer, nullable=False, default=0),
        sa.Column('total_output_tokens', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Index('idx_provider_cost_request', 'request_id'),
        sa.Index('idx_provider_cost_provider', 'provider_name'),
        sa.Index('idx_provider_cost_created', 'created_at'),
    )


def downgrade() -> None:
    """Remove provider_cost_breakdown table."""
    op.drop_table('provider_cost_breakdown')
