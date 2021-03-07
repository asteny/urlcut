import logging
from typing import List, Union

from asyncpg import Record
from asyncpgsa import pool
from sqlalchemy import and_, extract, select
from sqlalchemy.sql.expression import true
from sqlalchemy.dialects.postgresql import insert

from urlcut.models.db import links_table
from urlcut.models.urls import UrlCreateData
from urlcut.utils.generate_link import generate_link_path, salted_number


log = logging.getLogger(__name__)


async def get_url_short_path(
    db: pool, parsed_url_data: UrlCreateData
) -> Union[str, None]:
    async with db.acquire() as conn:
        return await conn.fetchval(
            select([links_table.c.short_url_path]).where(
                and_(
                    links_table.c.long_url == parsed_url_data.url,
                    links_table.c.name == parsed_url_data.name,
                    links_table.c.description == parsed_url_data.description,
                    links_table.c.labels == parsed_url_data.labels,
                )
            )
        )


async def insert_url_data(
    db: pool,
    alphabet: List,
    salt: int,
    pepper: int,
    parsed_url_data: UrlCreateData,
) -> Union[str, None]:
    async with db.transaction() as conn:
        next_seq_id = await conn.fetchval(
            "SELECT NEXTVAL('links_id_seq')",
            column=0,
        )
        log.debug("Next sequence id is %d", next_seq_id)

        short_url_path = generate_link_path(
            alphabet,
            salted_number(
                number=next_seq_id,
                salt=salt,
                pepper=pepper,
            ),
        )
        log.debug("Short link path is %r", short_url_path)

        id = await conn.fetchval(
            insert(links_table)
            .values(
                id=next_seq_id,
                name=parsed_url_data.name,
                description=parsed_url_data.description,
                long_url=parsed_url_data.url,
                short_url_path=short_url_path,
                not_active_after=parsed_url_data.notActiveAfter,
                labels=parsed_url_data.labels,
                creator=parsed_url_data.creator,
                active=parsed_url_data.active,
            )
            .returning(links_table.c.id)
            .on_conflict_do_nothing(constraint="uq__links__insert"),
        )

        if id:
            return short_url_path

        return None


async def deactivate_link(db: pool, short_path: str) -> bool:
    async with db.transaction() as conn:
        active_id_query = (
            select(
                [links_table.c.id],
            )
            .with_for_update(
                read=True,
            )
            .where(
                and_(
                    links_table.c.short_url_path == short_path,
                    links_table.c.active == true(),
                ),
            )
        )

        active_id = await conn.fetchval(active_id_query, column=0)
        log.debug("Active short link id is %r", active_id)

        if active_id:
            await conn.fetchrow(
                links_table.update()
                .where(
                    links_table.c.id == int(active_id),
                )
                .values(active=False),
            )
            log.info("Short link %r deactivated", short_path)
            return True

    return False


async def get_link_state(db: pool, short_path: str) -> Record:
    async with db.acquire() as conn:
        return await conn.fetchrow(
            select(
                [
                    links_table.c.long_url,
                    links_table.c.active,
                    extract(
                        "epoch",
                        links_table.c.not_active_after,
                    ).label("not_active_after"),
                ],
            ).where(
                links_table.c.short_url_path == short_path,
            ),
        )


async def get_link_by_short_path(db: pool, short_path: str) -> Record:
    async with db.acquire() as conn:
        return await conn.fetchrow(
            select(
                [
                    links_table.c.name,
                    links_table.c.description,
                    links_table.c.long_url,
                    links_table.c.short_url_path,
                    links_table.c.active,
                    extract(
                        "epoch",
                        links_table.c.not_active_after,
                    ).label("not_active_after"),
                    links_table.c.labels,
                    links_table.c.creator,
                    links_table.c.active,
                    extract(
                        "epoch",
                        links_table.c.created_at,
                    ).label("created_at"),
                    extract(
                        "epoch",
                        links_table.c.updated_at,
                    ).label("updated_at"),
                ],
            ).where(
                links_table.c.short_url_path == short_path,
            ),
        )
