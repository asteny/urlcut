import json
from http import HTTPStatus

from sqlalchemy import select
from yarl import URL

from urlcut.models.db import links_table
from urlcut.utils.generate_link import (
    generate_link, generate_link_path, salted_number,
)


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


async def test_create_valid(
        api_client, pg_engine, alphabet, domain, salt, pepper
):
    async with api_client.post(
            "api/create", json=get_json("tests/data/valid_url_post.json"),
    ) as response:
        async with pg_engine.acquire() as conn:
            last_seq_id = await conn.fetchval(
                "SELECT last_value FROM links_id_seq;", column=0,
            )

            salted_num = salted_number(
                number=last_seq_id,
                salt=salt,
                pepper=pepper,

            )

            link = generate_link(
                domain=domain,
                short_path=generate_link_path(
                    salted_num=salted_num,
                    alphabet=alphabet,
                ),
            )

            url_path = await conn.fetchrow(
                select([links_table.c.short_url_path]).where(
                    links_table.c.id == last_seq_id,
                ),
            )
            assert response.status == HTTPStatus.CREATED
            assert await response.json() == {"link": str(link)}
            assert url_path["short_url_path"] == str(URL(link).path).strip("/")


async def test_db(pg_engine):
    async with pg_engine.acquire() as conn:
        # uncomment for clear database
        # await pool.fetch("ALTER SEQUENCE links_id_seq RESTART WITH 1;")
        # await pool.fetch("DELETE FROM links;")
        result = await conn.execute(select([links_table]))
        assert result
