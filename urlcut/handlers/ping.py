import logging
from http import HTTPStatus

from aiohttp.web_response import json_response
from asyncpgsa import pool

from urlcut.handlers.base import Base


log = logging.getLogger(__name__)


class Ping(Base):
    __dependencies__ = ("db",)
    db: pool

    async def get(self):
        try:
            await self.db.fetch("SELECT 1")
            return json_response(
                status=HTTPStatus.OK,
                data={"pg_health": "alive"},
            )
        except Exception:
            log.exception("PG healthcheck error")
            return json_response(
                status=HTTPStatus.SERVICE_UNAVAILABLE,
                data={"pg_health": "dead"},
            )
