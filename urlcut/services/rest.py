import logging
from typing import List

from aiohttp.web import Application, normalize_path_middleware
from aiomisc.service.aiohttp import AIOHTTPService
from asyncpgsa import pool
from yarl import URL

from urlcut.handlers.ping import Ping
from urlcut.handlers.urls import Urls, UrlInfo
from urlcut.middleware import error_middleware


log = logging.getLogger(__name__)


class Rest(AIOHTTPService):
    __required__ = ("alphabet", "salt", "pepper", "domain")
    __dependencies__ = ("db",)

    alphabet: List[str]
    salt: int
    pepper: int
    domain: URL
    db: pool

    async def create_application(self):
        app = Application(
            middlewares=[
                error_middleware,
                normalize_path_middleware(
                    remove_slash=True,
                    append_slash=False,
                ),
            ]
        )
        router = app.router
        log.info("Starting API")

        app["alphabet"] = self.alphabet
        app["salt"] = self.salt
        app["pepper"] = self.pepper
        app["pepper"] = self.pepper
        app["domain"] = self.domain
        app["db"] = self.db

        router.add_route("GET", "/api/ping", Ping)
        router.add_route("POST", "/api/create", Urls)
        router.add_route("GET", r"/{short_path:[a-zA-Z0-9]+}", Urls)
        router.add_route("GET", r"/{short_path:[a-zA-Z0-9]+}/info", UrlInfo)
        router.add_route("DELETE", r"/{short_path:[a-zA-Z0-9]+}", Urls)

        return app
