"""Add is_current to LLMRecommendation so each user can mark one plan as current.

Revision ID: c4b7a1d2e9f3
Revises: 6d07969695ad
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4b7a1d2e9f3'
down_revision = '6d07969695ad'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('llm_recommendation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_current', sa.Boolean(), nullable=True))

    op.create_index(
        'uq_llm_recommendation_one_current_per_user',
        'llm_recommendation',
        ['user_id'],
        unique=True,
        sqlite_where=sa.text('is_current = 1'),
        postgresql_where=sa.text('is_current IS TRUE'),
    )


def downgrade():
    op.drop_index('uq_llm_recommendation_one_current_per_user', table_name='llm_recommendation')

    with op.batch_alter_table('llm_recommendation', schema=None) as batch_op:
        batch_op.drop_column('is_current')
