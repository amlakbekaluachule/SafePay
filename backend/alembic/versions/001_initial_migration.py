"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('card_id', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), server_default='USD'),
        sa.Column('merchant_id', sa.String(), nullable=False),
        sa.Column('merchant_category', sa.String(), nullable=False),
        sa.Column('transaction_type', sa.String(), nullable=False),
        sa.Column('location_country', sa.String(), nullable=False),
        sa.Column('location_city', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('device_id', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('raw_features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_timestamp', 'transactions', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_card_timestamp', 'transactions', ['card_id', 'timestamp'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_card_id'), 'transactions', ['card_id'], unique=False)
    op.create_index(op.f('ix_transactions_merchant_id'), 'transactions', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_transactions_timestamp'), 'transactions', ['timestamp'], unique=False)

    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('transaction_id', sa.String(), nullable=False),
        sa.Column('fraud_probability', sa.Float(), nullable=False),
        sa.Column('is_fraud', sa.Boolean(), nullable=False),
        sa.Column('threshold', sa.Float(), server_default='0.5'),
        sa.Column('shap_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('feature_contributions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('inference_time_ms', sa.Float(), nullable=True),
        sa.Column('actual_label', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index('idx_fraud_timestamp', 'predictions', ['is_fraud', 'created_at'], unique=False)
    op.create_index('idx_model_version', 'predictions', ['model_version'], unique=False)
    op.create_index(op.f('ix_predictions_transaction_id'), 'predictions', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_predictions_fraud_probability'), 'predictions', ['fraud_probability'], unique=False)
    op.create_index(op.f('ix_predictions_is_fraud'), 'predictions', ['is_fraud'], unique=False)
    op.create_index(op.f('ix_predictions_created_at'), 'predictions', ['created_at'], unique=False)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_action_timestamp', 'audit_logs', ['action', 'timestamp'], unique=False)
    op.create_index('idx_entity', 'audit_logs', ['entity_type', 'entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index('idx_entity', table_name='audit_logs')
    op.drop_index('idx_action_timestamp', table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index(op.f('ix_predictions_created_at'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_is_fraud'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_fraud_probability'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_transaction_id'), table_name='predictions')
    op.drop_index('idx_model_version', table_name='predictions')
    op.drop_index('idx_fraud_timestamp', table_name='predictions')
    op.drop_table('predictions')
    
    op.drop_index(op.f('ix_transactions_timestamp'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_merchant_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_card_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index('idx_card_timestamp', table_name='transactions')
    op.drop_index('idx_user_timestamp', table_name='transactions')
    op.drop_table('transactions')

