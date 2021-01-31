import logging
from typing import List

from aiohttp.web_urldispatcher import View
from asyncpgsa import pool


log = logging.getLogger(__name__)


class Base(View):
    @property
    def alphabet(self) -> List[str]:
        return self.request.app["alphabet"]

    @property
    def salt(self) -> int:
        return self.request.app["salt"]

    @property
    def pepper(self) -> int:
        return self.request.app["pepper"]

    @property
    def domain(self) -> pool:
        return self.request.app["domain"]

    @property
    def db(self) -> pool:
        return self.request.app["db"]
