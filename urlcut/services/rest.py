import logging
from typing import List

from aiohttp.web import Application
from aiomisc.service.aiohttp import AIOHTTPService
from asyncpgsa import pool
from yarl import URL

from urlcut.handlers.ping import Ping
from urlcut.handlers.urls import Urls


log = logging.getLogger(__name__)


class Rest(AIOHTTPService):
    __required__ = frozenset({"alphabet", "salt", "pepper", "domain"})
    __dependencies__ = ("db",)

    alphabet: List[str]
    salt: int
    pepper: int
    domain: URL
    db: pool

    async def create_application(self):
        app = Application()
        router = app.router

        log.info("Starting API")

        app["alphabet"] = self.alphabet
        app["salt"] = self.salt
        app["pepper"] = self.pepper
        app["pepper"] = self.pepper
        app["domain"] = self.domain
        app["db"] = self.db

        router.add_route("GET", "/ping", Ping)
        router.add_route("POST", "/create", Urls)
        router.add_route("DELETE", "/delete", Urls)

        return app