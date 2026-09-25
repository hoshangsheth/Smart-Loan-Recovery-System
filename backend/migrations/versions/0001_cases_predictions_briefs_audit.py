"""cases predictions briefs audit

Revision ID: 0001
Revises: 
Create Date: 2026-09-25 08:28:46.236370
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
TABLES = ("cases", "predictions", "case_briefs", "audit_log")

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('audit_log',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('actor_id', sa.String(length=64), nullable=False),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('entity_type', sa.String(length=32), nullable=False),
    sa.Column('entity_id', sa.String(length=36), nullable=False),
    sa.Column('details', JSON_TYPE, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_actor_id'), 'audit_log', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_log_created_at'), 'audit_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_log_entity_id'), 'audit_log', ['entity_id'], unique=False)
    op.create_table('cases',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('borrower_ref', sa.String(length=64), nullable=False),
    sa.Column('owner_id', sa.String(length=64), nullable=False),
    sa.Column('first_name', sa.String(length=80), nullable=False),
    sa.Column('last_name', sa.String(length=80), nullable=False),
    sa.Column('loan_type', sa.String(length=32), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cases_borrower_ref'), 'cases', ['borrower_ref'], unique=False)
    op.create_index(op.f('ix_cases_owner_id'), 'cases', ['owner_id'], unique=False)
    op.create_index(op.f('ix_cases_status'), 'cases', ['status'], unique=False)
    op.create_table('predictions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('case_id', sa.String(length=36), nullable=False),
    sa.Column('model_version', sa.String(length=32), nullable=False),
    sa.Column('risk_score', sa.Float(), nullable=False),
    sa.Column('risk_category', sa.String(length=64), nullable=False),
    sa.Column('strategy', sa.Text(), nullable=False),
    sa.Column('input', JSON_TYPE, nullable=False),
    sa.Column('calculated', JSON_TYPE, nullable=False),
    sa.Column('segment', JSON_TYPE, nullable=False),
    sa.Column('shap_top_features', JSON_TYPE, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_case_id'), 'predictions', ['case_id'], unique=False)
    op.create_index(op.f('ix_predictions_created_at'), 'predictions', ['created_at'], unique=False)
    op.create_table('case_briefs',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('case_id', sa.String(length=36), nullable=False),
    sa.Column('prediction_id', sa.String(length=36), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=False),
    sa.Column('llm_model', sa.String(length=64), nullable=False),
    sa.Column('prompt_version', sa.String(length=32), nullable=False),
    sa.Column('content', JSON_TYPE, nullable=False),
    sa.Column('latency_ms', sa.Integer(), nullable=False),
    sa.Column('input_tokens', sa.Integer(), nullable=True),
    sa.Column('output_tokens', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_briefs_case_id'), 'case_briefs', ['case_id'], unique=False)

    # Supabase exposes the public schema over PostgREST to anyone holding the
    # anon key (which ships in the frontend). RLS with no policies blocks that
    # path entirely; the backend connects as the table owner and is unaffected.
    if op.get_bind().dialect.name == "postgresql":
        for table in TABLES:
            op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_index(op.f('ix_case_briefs_case_id'), table_name='case_briefs')
    op.drop_table('case_briefs')
    op.drop_index(op.f('ix_predictions_created_at'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_case_id'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_cases_status'), table_name='cases')
    op.drop_index(op.f('ix_cases_owner_id'), table_name='cases')
    op.drop_index(op.f('ix_cases_borrower_ref'), table_name='cases')
    op.drop_table('cases')
    op.drop_index(op.f('ix_audit_log_entity_id'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_created_at'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_actor_id'), table_name='audit_log')
    op.drop_table('audit_log')
