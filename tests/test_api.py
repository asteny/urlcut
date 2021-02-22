import json
from http import HTTPStatus

from sqlalchemy import select

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


async def test_create_valid(api_client, pg_engine):
    async with api_client.post(
            "api/create", json=get_json("tests/data/valid_url_post.json"),
    ) as response:
        assert response.status == HTTPStatus.CREATED
        assert await response.json() == {
            "link": "http://example.com/CaCCgCaaaaAaAAAC",
        }

        async with pg_engine.acquire() as conn:
            short_url_path = await conn.fetchrow(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == 1,
                ),
            )
            assert short_url_path["short_url_path"] == "CaCCgCaaaaAaAAAC"


async def test_db(pg_engine):
    async with pg_engine.acquire() as conn:
        result = await conn.execute(select([links_table]))
        assert result
