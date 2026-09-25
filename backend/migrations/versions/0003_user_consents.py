"""user consents

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-25 13:08:04.462269
"""
from alembic import op
import sqlalchemy as sa


revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('user_consents',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=64), nullable=False),
    sa.Column('terms_version', sa.String(length=32), nullable=False),
    sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_agent', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_consents_user_id'), 'user_consents', ['user_id'], unique=False)
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE user_consents ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_index(op.f('ix_user_consents_user_id'), table_name='user_consents')
    op.drop_table('user_consents')
