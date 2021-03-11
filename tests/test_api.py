import json
from http import HTTPStatus

import pytest
from sqlalchemy import select
from yarl import URL

from urlcut.models.db import links_table


@pytest.fixture()
async def clear_db(pg_engine):
    await pg_engine.fetch("ALTER SEQUENCE links_id_seq RESTART WITH 1;")
    await pg_engine.fetch("DELETE FROM links;")


@pytest.fixture()
async def create_valid_link(api_client):
    resp = await api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post.json"),
    )
    return URL(
        (await resp.json()).get("link"),
    )


@pytest.fixture()
async def create_valid_link_with_new_name(api_client):
    resp = await api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post_new_name.json"),
    )
    return resp


@pytest.fixture()
async def create_not_valid_after_link(api_client):
    resp = await api_client.post(
        "api/create",
        json=get_json(
            "tests/data/valid_url_post_not_valid_after.json",
        ),
    )
    return URL(
        (await resp.json()).get("link"),
    )


@pytest.fixture()
async def without_not_activ_after_link(api_client):
    resp = await api_client.post(
        "api/create",
        json=get_json(
            "tests/data/valid_url_post_without_not_activ_after.json",
        ),
    )
    return URL(
        (await resp.json()).get("link"),
    )


@pytest.fixture()
async def create_valid_not_active_link(api_client):
    resp = await api_client.post(
        "api/create",
        json=get_json(
            "tests/data/valid_url_post_not_active.json",
        ),
    )
    return URL(
        (await resp.json()).get("link"),
    )


def get_json(file: str):
    with open(file) as json_file:
        data = json.load(json_file)
    return data


async def test_ping(api_client):
    async with api_client.get(
        "api/ping",
    ) as response:
        assert response.status == HTTPStatus.OK
        assert await response.json() == {"pg_health": "alive"}


async def test_wrong_method(api_client):
    async with api_client.delete(
        "api/ping",
    ) as response:
        assert response.status == HTTPStatus.METHOD_NOT_ALLOWED
        assert await response.json() == {"error": "405: Method Not Allowed"}


async def test_create_not_valid(api_client):

    async with api_client.post(
        "api/create",
        json=get_json("tests/data/not_valid_url_post.json"),
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == get_json(
            "tests/data/not_valid_url_post_resp.json",
        )


async def test_create_without_data(api_client):
    async with api_client.post(
        "api/create",
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {"error": "Failed to decode json"}


async def test_create_valid(api_client, clear_db, pg_engine):
    async with api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;",
                column=0,
            )

            assert last_seq_id == 1

            url_path = await conn.fetchrow(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == last_seq_id,
                ),
            )

            assert response.status == HTTPStatus.CREATED
            assert await response.json() == {
                "link": "http://example.com/CaCCgCaaaaAaAAAC",
            }
            assert url_path["short_url_path"] == "CaCCgCaaaaAaAAAC"


async def test_idempotent_create(
    api_client, clear_db, create_valid_link, pg_engine
):
    async with api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;",
                column=0,
            )
            assert last_seq_id == 2

            url_path = await conn.fetchval(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == 1,
                ),
            )

            assert response.status == HTTPStatus.OK
            assert await response.json() == {
                "link": "http://example.com/CaCCgCaaaaAaAAAC",
            }
            assert url_path == "CaCCgCaaaaAaAAAC"


async def test_create_with_new_name(
    api_client, clear_db, create_valid_link, pg_engine
):
    async with api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post_new_name.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;",
                column=0,
            )

            assert last_seq_id == 2

            url_path = await conn.fetchval(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == last_seq_id,
                ),
            )

            assert response.status == HTTPStatus.CREATED
            assert await response.json() == {
                "link": "http://example.com/CaCCgCaaaaAaAAAA",
            }
            assert url_path == "CaCCgCaaaaAaAAAA"


async def test_create_repeat_with_new_name(
    api_client,
    clear_db,
    create_valid_link,
    create_valid_link_with_new_name,
    pg_engine,
):
    async with api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post_new_name.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;",
                column=0,
            )

            assert last_seq_id == 3

            url_path = await conn.fetchval(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == 2,
                ),
            )

            assert response.status == HTTPStatus.OK
            assert await response.json() == {
                "link": "http://example.com/CaCCgCaaaaAaAAAA",
            }
            assert url_path == "CaCCgCaaaaAaAAAA"


async def test_unique_constraint(
    api_client,
    clear_db,
    create_valid_link,
    create_valid_link_with_new_name,
    pg_engine,
):
    async with api_client.post(
        "api/create",
        json=get_json("tests/data/valid_url_post_new_url.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;",
                column=0,
            )

            assert last_seq_id == 3

            url_path = await conn.fetchval(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == 3,
                ),
            )

            assert response.status == HTTPStatus.CREATED
            assert await response.json() == {
                "link": "http://example.com/CaCCgCaaaaAaAAAa",
            }
            assert url_path == "CaCCgCaaaaAaAAAa"


async def test_delete(api_client, clear_db, create_valid_link, pg_engine):
    path_from_created_link = create_valid_link.path.lstrip("/")

    async with api_client.delete(
        path_from_created_link,
    ) as response:
        assert response.status == HTTPStatus.NO_CONTENT

    active = await pg_engine.fetchval(
        select([links_table.c.active]).where(
            links_table.c.short_url_path == path_from_created_link,
        ),
    )
    assert active is False


@pytest.mark.parametrize("url_path", ["azaza", "12345", "asas11", "33asas11"])
async def test_delete_not_found(api_client, url_path):
    async with api_client.delete(
        url_path,
    ) as response:
        assert response.status == HTTPStatus.NO_CONTENT


async def test_get_absent_link(api_client):
    async with api_client.get(
        "someLink",
    ) as response:
        assert response.status == HTTPStatus.NOT_FOUND


async def test_get_link(api_client, clear_db, create_valid_link):
    path_from_created_link = create_valid_link.path.lstrip("/")
    async with api_client.get(
        path_from_created_link,
        allow_redirects=False,
    ) as response:
        assert response.status == HTTPStatus.MOVED_PERMANENTLY
        assert (
            response.headers.get(
                "Location",
            )
            == "https://example.com/fiz/baz/ololo"
        )


async def test_get_not_valid_after_link(
    api_client, clear_db, create_not_valid_after_link
):
    path_from_created_link = create_not_valid_after_link.path.lstrip("/")
    async with api_client.get(path_from_created_link) as response:
        assert response.status == HTTPStatus.GONE


async def test_get_not_active_link(
    api_client, clear_db, create_valid_not_active_link
):
    path_from_created_link = create_valid_not_active_link.path.lstrip("/")
    async with api_client.get(path_from_created_link) as response:
        assert response.status == HTTPStatus.GONE


async def test_get_link_info(api_client, clear_db, create_valid_link):
    short_url_path = "CaCCgCaaaaAaAAAC"
    async with api_client.get(
        f"{short_url_path}/info",
    ) as response:
        assert response.status == HTTPStatus.OK

        resp = await response.json()
        assert resp.get("short_url_path") == short_url_path


async def test_get_link_info_not_found(
    api_client, clear_db, create_valid_link
):
    async with api_client.get(
        "azaza/info",
    ) as response:
        assert response.status == HTTPStatus.NOT_FOUND


async def test_trailing_slash(api_client, clear_db, create_valid_link):
    short_url_path = "CaCCgCaaaaAaAAAC"
    async with api_client.get(
        f"{short_url_path}/info/",
    ) as response:
        assert response.status == HTTPStatus.OK

        resp = await response.json()
        assert resp.get("short_url_path") == short_url_path


async def test_trailing_slash_without_redirect(
    api_client, clear_db, create_valid_link
):
    async with api_client.get(
        "CaCCgCaaaaAaAAAC/info/?key=value", allow_redirects=False
    ) as response:
        assert response.status == HTTPStatus.PERMANENT_REDIRECT

        location = response.headers["Location"]
        assert location == "/CaCCgCaaaaAaAAAC/info?key=value"


async def test_update_without_data(api_client):
    async with api_client.put(
        "CaCCgCaaaaAaAAAC",
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {"error": "Failed to decode json"}


async def test_update_valid(
    api_client, clear_db, create_valid_link, pg_engine
):
    async with api_client.put(
        "CaCCgCaaaaAaAAAC",
        json=get_json("tests/data/valid_url_put.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            description = await conn.fetchval(
                select([links_table.c.description]).where(
                    links_table.c.id == 1,
                ),
            )

            assert response.status == HTTPStatus.CREATED
            assert description == "Updated description"


async def test_update_not_valid(
    api_client, clear_db, create_valid_link, pg_engine
):
    async with api_client.put(
        "CaCCgCaaaaAaAAAC",
        json=get_json("tests/data/not_valid_url_put.json"),
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST
