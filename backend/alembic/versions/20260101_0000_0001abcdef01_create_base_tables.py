"""create_base_tables

Revision ID: 0001abcdef01
Revises:
Create Date: 2026-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '0001abcdef01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- operators ---
    op.create_table('operators',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('station_id', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.CheckConstraint(
            "role IN ('operator', 'quality_inspector', 'supervisor', 'admin')",
            name='check_operator_role'
        ),
    )
    op.create_index(op.f('ix_operators_username'), 'operators', ['username'], unique=True)
    op.create_index(op.f('ix_operators_role'), 'operators', ['role'], unique=False)
    op.create_index(op.f('ix_operators_is_active'), 'operators', ['is_active'], unique=False)

    # --- products ---
    op.create_table('products',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('product_code', sa.String(length=100), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('production_target', sa.Integer(), nullable=True),
        sa.Column('target_status', sa.String(length=50), nullable=False, server_default='not_set'),
        sa.Column('target_set_at', sa.DateTime(), nullable=True),
        sa.Column('target_completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_code'),
        sa.CheckConstraint(
            "target_status IN ('not_set', 'in_progress', 'completed')",
            name='check_target_status'
        ),
    )
    op.create_index(op.f('ix_products_product_code'), 'products', ['product_code'], unique=True)
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'], unique=False)

    # --- production_stages ---
    op.create_table('production_stages',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('stage_name', sa.String(length=100), nullable=False),
        sa.Column('stage_sequence', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stage_name'),
        sa.UniqueConstraint('stage_sequence'),
    )
    op.create_index(op.f('ix_production_stages_stage_name'), 'production_stages', ['stage_name'], unique=True)
    op.create_index(op.f('ix_production_stages_stage_sequence'), 'production_stages', ['stage_sequence'], unique=True)

    # --- work_orders ---
    op.create_table('work_orders',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('work_order_code', sa.String(length=50), nullable=False),
        sa.Column('serial_number', sa.String(length=10), nullable=False),
        sa.Column('product_id', UUID(as_uuid=True), nullable=True),
        sa.Column('current_stage_id', UUID(as_uuid=True), nullable=True),
        sa.Column('overall_quality_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['current_stage_id'], ['production_stages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('work_order_code'),
        sa.CheckConstraint(
            "LENGTH(work_order_code) BETWEEN 20 AND 50",
            name='check_work_order_code_length'
        ),
        sa.CheckConstraint(
            "overall_quality_status IN ('pending', 'ok', 'not_ok')",
            name='check_overall_quality_status'
        ),
    )
    op.create_index(op.f('ix_work_orders_work_order_code'), 'work_orders', ['work_order_code'], unique=True)
    op.create_index(op.f('ix_work_orders_serial_number'), 'work_orders', ['serial_number'], unique=False)
    op.create_index(op.f('ix_work_orders_current_stage_id'), 'work_orders', ['current_stage_id'], unique=False)
    op.create_index(op.f('ix_work_orders_overall_quality_status'), 'work_orders', ['overall_quality_status'], unique=False)
    op.create_index(op.f('ix_work_orders_created_at'), 'work_orders', ['created_at'], unique=False)

    # --- scan_records (without supervisor_id — added by next migration) ---
    op.create_table('scan_records',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('work_order_id', UUID(as_uuid=True), nullable=False),
        sa.Column('stage_id', UUID(as_uuid=True), nullable=False),
        sa.Column('operator_id', UUID(as_uuid=True), nullable=False),
        sa.Column('scan_type', sa.String(length=50), nullable=False),
        sa.Column('quality_status', sa.String(length=50), nullable=False),
        sa.Column('is_first_article', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('quality_inspector_id', UUID(as_uuid=True), nullable=True),
        sa.Column('previous_quality_status', sa.String(length=50), nullable=True),
        sa.Column('scan_timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stage_id'], ['production_stages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['quality_inspector_id'], ['operators.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('work_order_id', 'stage_id', name='uq_work_order_stage'),
        sa.CheckConstraint(
            "scan_type IN ('normal', 'first_article', 'update')",
            name='check_scan_type'
        ),
        sa.CheckConstraint(
            "quality_status IN ('ok', 'not_ok', 'ok_update', 'not_ok_update')",
            name='check_quality_status'
        ),
    )
    op.create_index(op.f('ix_scan_records_work_order_id'), 'scan_records', ['work_order_id'], unique=False)
    op.create_index(op.f('ix_scan_records_stage_id'), 'scan_records', ['stage_id'], unique=False)
    op.create_index(op.f('ix_scan_records_operator_id'), 'scan_records', ['operator_id'], unique=False)
    op.create_index(op.f('ix_scan_records_quality_status'), 'scan_records', ['quality_status'], unique=False)
    op.create_index(op.f('ix_scan_records_is_first_article'), 'scan_records', ['is_first_article'], unique=False)
    op.create_index(op.f('ix_scan_records_scan_timestamp'), 'scan_records', ['scan_timestamp'], unique=False)

    # --- quality_status_log ---
    op.create_table('quality_status_log',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('scan_record_id', UUID(as_uuid=True), nullable=False),
        sa.Column('work_order_id', UUID(as_uuid=True), nullable=False),
        sa.Column('stage_id', UUID(as_uuid=True), nullable=False),
        sa.Column('operator_id', UUID(as_uuid=True), nullable=False),
        sa.Column('previous_status', sa.String(length=50), nullable=False),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['scan_record_id'], ['scan_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stage_id'], ['production_stages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "previous_status IN ('ok', 'not_ok', 'ok_update', 'not_ok_update')",
            name='check_previous_status'
        ),
        sa.CheckConstraint(
            "new_status IN ('ok', 'not_ok', 'ok_update', 'not_ok_update')",
            name='check_new_status'
        ),
        sa.CheckConstraint(
            "previous_status != new_status",
            name='check_status_different'
        ),
    )
    op.create_index(op.f('ix_quality_status_log_scan_record_id'), 'quality_status_log', ['scan_record_id'], unique=False)
    op.create_index(op.f('ix_quality_status_log_work_order_id'), 'quality_status_log', ['work_order_id'], unique=False)
    op.create_index(op.f('ix_quality_status_log_operator_id'), 'quality_status_log', ['operator_id'], unique=False)
    op.create_index(op.f('ix_quality_status_log_changed_at'), 'quality_status_log', ['changed_at'], unique=False)

    # --- rework_costs ---
    op.create_table('rework_costs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('stage_id', UUID(as_uuid=True), nullable=False),
        sa.Column('cost_per_rework', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('effective_from', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['stage_id'], ['production_stages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stage_id'),
        sa.CheckConstraint(
            "cost_per_rework >= 0",
            name='check_cost_non_negative'
        ),
    )
    op.create_index(op.f('ix_rework_costs_stage_id'), 'rework_costs', ['stage_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_rework_costs_stage_id'), table_name='rework_costs')
    op.drop_table('rework_costs')

    op.drop_index(op.f('ix_quality_status_log_changed_at'), table_name='quality_status_log')
    op.drop_index(op.f('ix_quality_status_log_operator_id'), table_name='quality_status_log')
    op.drop_index(op.f('ix_quality_status_log_work_order_id'), table_name='quality_status_log')
    op.drop_index(op.f('ix_quality_status_log_scan_record_id'), table_name='quality_status_log')
    op.drop_table('quality_status_log')

    op.drop_index(op.f('ix_scan_records_scan_timestamp'), table_name='scan_records')
    op.drop_index(op.f('ix_scan_records_is_first_article'), table_name='scan_records')
    op.drop_index(op.f('ix_scan_records_quality_status'), table_name='scan_records')
    op.drop_index(op.f('ix_scan_records_operator_id'), table_name='scan_records')
    op.drop_index(op.f('ix_scan_records_stage_id'), table_name='scan_records')
    op.drop_index(op.f('ix_scan_records_work_order_id'), table_name='scan_records')
    op.drop_table('scan_records')

    op.drop_index(op.f('ix_work_orders_created_at'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_overall_quality_status'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_current_stage_id'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_serial_number'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_work_order_code'), table_name='work_orders')
    op.drop_table('work_orders')

    op.drop_index(op.f('ix_production_stages_stage_sequence'), table_name='production_stages')
    op.drop_index(op.f('ix_production_stages_stage_name'), table_name='production_stages')
    op.drop_table('production_stages')

    op.drop_index(op.f('ix_products_is_active'), table_name='products')
    op.drop_index(op.f('ix_products_product_code'), table_name='products')
    op.drop_table('products')

    op.drop_index(op.f('ix_operators_is_active'), table_name='operators')
    op.drop_index(op.f('ix_operators_role'), table_name='operators')
    op.drop_index(op.f('ix_operators_username'), table_name='operators')
    op.drop_table('operators')
