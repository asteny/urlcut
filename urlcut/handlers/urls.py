import logging
from datetime import datetime
from http import HTTPStatus

from aiohttp.web_response import json_response

from urlcut.handlers.base import Base
from urlcut.models.db_query import (
    deactivate_link, get_link_state, insert_url_data,
)
from urlcut.models.urls import UrlCreateData
from urlcut.utils.generate_link import generate_link


log = logging.getLogger(__name__)


class Urls(Base):
    async def post(self):
        data = await self.request.json()
        log.debug("Url data from post request is %r", data)

        parsed_url_data = UrlCreateData(**data)
        log.debug("Parsed url_data is %r", parsed_url_data)

        short_url_path = await insert_url_data(
            db=self.db,
            alphabet=self.alphabet,
            salt=self.salt,
            pepper=self.pepper,
            parsed_url_data=parsed_url_data,
        )

        generated_link = generate_link(
            domain=self.domain, short_path=short_url_path,
        )

        return json_response(
            status=HTTPStatus.CREATED,
            data={"link": str(generated_link)},

        )

    async def get(self):
        short_path = self.request.match_info["short_path"]
        log.debug("Short link from get request is %r", short_path)

        link_state = await get_link_state(self.db, short_path=short_path)

        if not link_state:
            log.debug("Link: %r not found", short_path)
            return json_response(status=HTTPStatus.NOT_FOUND)

        redirect_link, acive, not_active_after = link_state

        if not all((
                acive,
                not_active_after is None or
                not_active_after > datetime.timestamp(datetime.now()),
        )):
            log.debug("Link: %r was deactivated", short_path)
            return json_response(status=HTTPStatus.GONE)

        log.info("Redirecting to %r", redirect_link)
        return json_response(
            status=HTTPStatus.MOVED_PERMANENTLY,
            headers={"Location": redirect_link},
        )

    async def delete(self):
        short_path = self.request.match_info["short_path"]
        log.debug("Short link from delete request is %r", short_path)

        if not await deactivate_link(self.db, short_path):
            log.info("%r not found", short_path)

        return json_response(status=HTTPStatus.NO_CONTENT)
