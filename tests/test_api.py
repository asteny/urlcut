from http import HTTPStatus


async def test_ping(api_client):
    async with api_client.get(
            "api/ping",
    ) as response:
        print(response)
        assert response.status == HTTPStatus.OK
        assert await response.json() == {"pg_health": "alive"}
