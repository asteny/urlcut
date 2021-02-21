"""Init

Revision ID: cb3f0359d7b5
Revises:
Create Date: 2021-01-31 12:31:08.549329

"""
from sqlalchemy import (
    TIMESTAMP, Boolean, Column, Integer, PrimaryKeyConstraint, String,
    UniqueConstraint, text,
)
from sqlalchemy.dialects import postgresql as pg

from alembic import op


# revision identifiers, used by Alembic.
revision = "cb3f0359d7b5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "links",
        Column("id", Integer(), nullable=False),
        Column("name", String(length=50), nullable=False),
        Column("description", String(length=300), nullable=True),
        Column("long_url", String(length=2000), nullable=False),
        Column(
            "short_url_path", String(length=50), nullable=False, unique=True,
        ),
        Column("not_active_after", TIMESTAMP(timezone=True), nullable=True),
        Column("labels", pg.ARRAY(String), nullable=True),
        Column("creator", String(length=50), nullable=True),
        Column("active", Boolean(), nullable=False),
        Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=text("timezone('utc', now())"),
            nullable=False,
        ),
        Column(
            "updated_at",
            TIMESTAMP(timezone=True),
            server_default=text("timezone('utc', now())"),
            nullable=False,
        ),
        PrimaryKeyConstraint("id", name=op.f("pk__groups")),
        UniqueConstraint("short_url_path", name=op.f("uq__groups__group_id")),
    )


def downgrade():
    op.drop_table("links")
