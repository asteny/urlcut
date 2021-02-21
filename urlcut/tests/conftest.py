import os
import pytest

from yarl import URL
from asyncpgsa import create_pool


@pytest.fixture()
async def domain():
    return URL(os.environ.get("URLCUT_DOMAIN"))


@pytest.fixture()
async def alphabet():
    return list(os.environ.get("URLCUT_ALPHABET"))


@pytest.fixture()
async def pepper():
    return int(os.environ.get("URLCUT_PEPPER"))


@pytest.fixture()
async def salt():
    return int(os.environ.get("URLCUT_SALT"))


@pytest.fixture()
async def pg_url():
    return URL(os.environ.get("URLCUT_PG_URL"))


@pytest.fixture()
async def pg_engine(pg_url):
    pool = await create_pool(
        dsn=str(pg_url),
        min_size=1,
        max_size=2
    )

    await pool.fetch("SELECT 1")

    try:
        yield pool
    finally:
        await pool.close()
