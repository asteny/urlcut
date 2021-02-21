import os
import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_app import Application
from aiomisc import bind_socket
from urlcut.deps import setup_dependencies

from urlcut.services.rest import Rest
from urlcut.main import parser

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


@pytest.fixture
def arguments(
        domain,
        alphabet,
        salt,
        pepper,
        pg_url
):
    return parser.parse_args(
        [
            "--log-level=debug",
            f"--domain={domain}",
            f"--alphabet={alphabet}",
            f"--salt={salt}",
            f"--pepper={pepper}",
            f"--pg-url={pg_url}",
        ]
    )


@pytest.fixture
def rest(arguments):
    setup_dependencies(arguments)
    socket = bind_socket(
        address=arguments.address,
        port=arguments.port,
        proto_name="http",
    )
    return Rest(
        sock=socket,
        alphabet=arguments.alphabet,
        salt=arguments.salt,
        pepper=arguments.pepper,
        domain=arguments.domain,
    )


@pytest.fixture
def services(rest):
    return [rest]


@pytest.fixture()
async def api_client(rest_url):
    server = TestServer(Application())
    server._root = URL.build(
        scheme="http", host=rest_url.host, port=rest_url.port
    )
    client = TestClient(server)
    try:
        yield client
    finally:
        await client.close()
