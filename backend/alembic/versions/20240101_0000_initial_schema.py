"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    
    # Create index on email for faster lookups
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create requests table
    op.create_table(
        'requests',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('execution_mode', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes on requests table
    op.create_index('ix_requests_user_id', 'requests', ['user_id'])
    op.create_index('ix_requests_created_at', 'requests', ['created_at'])
    op.create_index('ix_requests_status', 'requests', ['status'])
    
    # Create responses table
    op.create_table(
        'responses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('request_id', UUID(as_uuid=True), sa.ForeignKey('requests.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=False),
        sa.Column('execution_time', sa.Float(), nullable=False),
        sa.Column('models_used', JSONB(), nullable=False),
        sa.Column('orchestration_metadata', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create index on request_id for faster lookups
    op.create_index('ix_responses_request_id', 'responses', ['request_id'])
    
    # Create subtasks table
    op.create_table(
        'subtasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('request_id', UUID(as_uuid=True), sa.ForeignKey('requests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=False),
        sa.Column('priority', sa.String(50), nullable=False),
        sa.Column('assigned_model', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes on subtasks table
    op.create_index('ix_subtasks_request_id', 'subtasks', ['request_id'])
    op.create_index('ix_subtasks_status', 'subtasks', ['status'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('subtasks')
    op.drop_table('responses')
    op.drop_table('requests')
    op.drop_table('users')
