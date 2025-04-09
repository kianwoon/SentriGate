"""Create audit_logs table

Revision ID: create_audit_log_table
Revises: <previous_revision_id>
Create Date: 2023-XX-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'create_audit_log_table'
down_revision = '<previous_revision_id>'  # Replace with your actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('token_id', sa.Integer(), sa.ForeignKey('tokens.id'), nullable=False),
        sa.Column('collection_name', sa.String(255), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('filter_data', JSONB, nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('response_data', JSONB, nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Add index for faster queries
    op.create_index(op.f('ix_audit_logs_token_id'), 'audit_logs', ['token_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_token_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
