import logging
from http import HTTPStatus

from aiohttp.web_response import json_response

from urlcut.handlers.base import Base
from urlcut.models.db_query import deactivate_link, insert_url_data
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

    async def delete(self):
        short_path = self.request.match_info["short_path"]
        log.debug("Short link from request is %r", short_path)

        if not await deactivate_link(self.db, short_path):
            log.info("%r not found", short_path)

        return json_response(status=HTTPStatus.NO_CONTENT)
