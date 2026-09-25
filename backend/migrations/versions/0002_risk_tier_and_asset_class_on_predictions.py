"""risk tier and asset class on predictions

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-25 12:59:07.564050
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('risk_tier', sa.String(length=32), nullable=True))
    op.add_column('predictions', sa.Column('risk_band', sa.String(length=16), nullable=True))
    op.add_column('predictions', sa.Column('asset_classification', sa.String(length=16), nullable=True))
    op.add_column('predictions', sa.Column('policy_override', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'policy_override')
    op.drop_column('predictions', 'asset_classification')
    op.drop_column('predictions', 'risk_band')
    op.drop_column('predictions', 'risk_tier')
