import json
import pytest
from http import HTTPStatus


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


@pytest.mark.parametrize(
    "req_data, exp_resp",
    [
        (
            get_json("tests/data/not_valid_url_post.json"),
            json.dumps(get_json("tests/data/not_valid_url_post_resp.json"))
        ),
    ],
)
async def test_create(api_client, req_data, exp_resp):
    async with api_client.post(
            "api/create", json=req_data
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == exp_resp


async def test_create_without_data(api_client):
    async with api_client.post(
            "api/create",
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == json.dumps(
            {"error": "Failed to decode json"}
        )
