"""add water glasses to nutrition log

Revision ID: a1b2c3d4e5f6
Revises: 3dd894352f8e
Create Date: 2026-05-03 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "3dd894352f8e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("nutrition_log", schema=None) as batch_op:
        batch_op.add_column(sa.Column("water_glasses", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("nutrition_log", schema=None) as batch_op:
        batch_op.drop_column("water_glasses")
