import json
from http import HTTPStatus

import pytest
from sqlalchemy import select
from yarl import URL

from urlcut.models.db import links_table


def get_json(file):
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
            "api/create", json=get_json("tests/data/not_valid_url_post.json"),
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


@pytest.fixture()
async def clear_db(pg_engine):
    await pg_engine.fetch("ALTER SEQUENCE links_id_seq RESTART WITH 1;")
    await pg_engine.fetch("DELETE FROM links;")


async def test_create_valid(
        api_client, clear_db, pg_engine
):
    async with api_client.post(
            "api/create", json=get_json("tests/data/valid_url_post.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;", column=0,
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


@pytest.fixture()
async def create_link(api_client):
    resp = await api_client.post(
        "api/create", json=get_json("tests/data/valid_url_post.json"),
    )
    return URL(
        (await resp.json()).get("link"),
    )


async def test_delete(api_client, create_link, pg_engine):
    path_from_created_link = create_link.path.lstrip("/")

    async with api_client.delete(
            f"api/delete/{path_from_created_link}",
    ) as response:
        assert response.status == HTTPStatus.NO_CONTENT

    active = await pg_engine.fetchval(
        select([links_table.c.active]).where(
                links_table.c.short_url_path == path_from_created_link,
        ),
    )
    assert active is False


async def test_delete_not_found(api_client):
    async with api_client.delete(
            "api/delete/azaza",
    ) as response:
        assert response.status == HTTPStatus.NO_CONTENT


async def test_delete_non_alphabet(api_client):
    async with api_client.delete(
            "api/delete/12345",
    ) as response:
        assert response.status == HTTPStatus.NOT_FOUND
