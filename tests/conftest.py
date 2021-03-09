import os

import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_app import Application
from aiomisc import bind_socket
from asyncpgsa import create_pool
from yarl import URL

from urlcut.deps import setup_dependencies
from urlcut.main import parser
from urlcut.services.rest import Rest


@pytest.fixture()
def domain():
    return URL(os.environ.get("URLCUT_DOMAIN", "http://example.com"))


@pytest.fixture()
def alphabet():
    return list(os.environ.get("URLCUT_ALPHABET", "aACg"))


@pytest.fixture()
def pepper():
    return int(os.environ.get("URLCUT_PEPPER", 2222))


@pytest.fixture()
def salt():
    return int(os.environ.get("URLCUT_SALT", 1111))


@pytest.fixture()
def pg_url():
    return URL(
        os.environ.get(
            "URLCUT_PG_URL", "postgresql://urlcut:12345@localhost:5432/urlcut"
        )
    )


@pytest.fixture()
def localhost():
    return os.environ.get("URLCUT_LOCALHOST", "0.0.0.0")


@pytest.fixture()
async def pg_engine(pg_url):
    pool = await create_pool(
        dsn=str(pg_url),
        min_size=1,
        max_size=2,
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
    pg_url,
):
    return parser.parse_args(
        [
            "--log-level=debug",
            f"--domain={domain}",
            "--alphabet",
            *alphabet,
            f"--salt={salt}",
            f"--pepper={pepper}",
            f"--pg-url={pg_url}",
        ],
    )


@pytest.fixture
async def rest(arguments, rest_url):
    setup_dependencies(arguments)
    socket = bind_socket(
        address=rest_url.host,
        port=rest_url.port,
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
async def services(rest):
    return [rest]


@pytest.fixture
def rest_url(localhost, aiomisc_unused_port_factory):
    return URL.build(
        scheme="http",
        host=localhost,
        port=aiomisc_unused_port_factory(),
    )


@pytest.fixture()
async def api_client(rest_url):
    server = TestServer(Application())
    server._root = rest_url
    client = TestClient(server)
    try:
        yield client
    finally:
        await client.close()
