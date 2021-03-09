import logging
from argparse import Namespace

from aiomisc_dependency import dependency
from asyncpgsa import create_pool


log = logging.getLogger(__name__)


def setup_dependencies(arguments: Namespace):
    @dependency
    async def db(loop):
        db_info = arguments.pg_url.with_password("***")
        pool = await create_pool(
            dsn=str(arguments.pg_url),
            min_size=arguments.pg_min_pool_size,
            max_size=arguments.pg_max_pool_size,
            loop=loop,
        )

        await pool.fetch("SELECT 1")
        log.info("Connected to database %s", db_info)

        try:
            yield pool
        finally:
            log.info("Disconnecting from database %s", db_info)
            await pool.close()
            log.info("Disconnected from database %s", db_info)
