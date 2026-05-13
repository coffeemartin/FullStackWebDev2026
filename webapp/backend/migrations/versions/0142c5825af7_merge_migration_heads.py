"""merge migration heads

Revision ID: 0142c5825af7
Revises: b4c5d6e7f8a9, c4b7a1d2e9f3
Create Date: 2026-05-12 20:25:10.662078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0142c5825af7'
down_revision = ('b4c5d6e7f8a9', 'c4b7a1d2e9f3')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
