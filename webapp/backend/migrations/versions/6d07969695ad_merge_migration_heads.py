"""merge migration heads

Revision ID: 6d07969695ad
Revises: 9f4a04e88064, a1b2c3d4e5f6
Create Date: 2026-05-06 14:48:33.743189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d07969695ad'
down_revision = ('9f4a04e88064', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
