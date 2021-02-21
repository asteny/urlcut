import logging
from typing import List

from asyncpgsa import pool

from urlcut.models.db import links_table
from urlcut.models.urls import UrlCreateData
from urlcut.utils.generate_link import generate_link_path, salted_number


log = logging.getLogger(__name__)


async def insert_url_data(
        db: pool,
        alphabet: List,
        salt: int,
        pepper: int,
        parsed_url_data: UrlCreateData
) -> str:
    try:
        async with db.transaction() as conn:
            next_seq_id = await conn.fetchval(
                f"SELECT NEXTVAL('links_id_seq')", column=0,
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

            await conn.fetchrow(
                links_table.insert().values(
                    id=next_seq_id,
                    name=parsed_url_data.name,
                    description=parsed_url_data.description,
                    long_url=parsed_url_data.url,
                    short_url_path=short_url_path,
                    not_active_after=parsed_url_data.notActiveAfter,
                    labels=parsed_url_data.labels,
                    creator=parsed_url_data.creator,
                    active=True,
                ),
            )

            return short_url_path
    except Exception as e:
        log.exception(e)
