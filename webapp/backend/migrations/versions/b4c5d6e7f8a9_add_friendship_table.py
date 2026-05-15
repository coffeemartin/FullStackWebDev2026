"""add friendship table

Revision ID: b4c5d6e7f8a9
Revises: 9ddc0bcbc1ca
Create Date: 2026-05-11 13:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b4c5d6e7f8a9"
down_revision = "9ddc0bcbc1ca"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "friendship",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("receiver_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("requester_id != receiver_id", name="ck_friendship_not_self"),
        sa.ForeignKeyConstraint(["receiver_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["requester_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("requester_id", "receiver_id", name="uq_friendship_request_pair"),
    )
    with op.batch_alter_table("friendship", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_friendship_receiver_id"), ["receiver_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_friendship_requester_id"), ["requester_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_friendship_status"), ["status"], unique=False)


def downgrade():
    with op.batch_alter_table("friendship", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_friendship_status"))
        batch_op.drop_index(batch_op.f("ix_friendship_requester_id"))
        batch_op.drop_index(batch_op.f("ix_friendship_receiver_id"))
    op.drop_table("friendship")
