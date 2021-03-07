from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    func,
)
from sqlalchemy.dialects import postgresql as pg


convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()],
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


links_table = Table(
    "links",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("description", String(300)),
    Column("long_url", String(2000), nullable=False),
    Column("short_url_path", String(50), nullable=False, unique=True),
    Column("not_active_after", TIMESTAMP(timezone=True), nullable=True),
    Column("labels", pg.ARRAY(String)),
    Column("creator", String(50), nullable=True),
    Column("active", Boolean, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.timezone("utc", func.now()),
    ),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    ),
)
