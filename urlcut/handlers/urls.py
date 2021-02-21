import logging
from http import HTTPStatus

from aiohttp.web_response import Response, json_response

from urlcut.handlers.base import Base
from urlcut.models.db_query import insert_url_data
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

        if not short_url_path:
            return Response(
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            )

        generated_link = generate_link(
            domain=self.domain, short_path=short_url_path,
        )

        return json_response(
            status=HTTPStatus.CREATED,
            data={"link": str(generated_link)},

        )

    async def delete(self):
        data = await self.request.json()
        log.debug("Delete data is %r", data)

        # TODO: write method
        return Response(status=HTTPStatus.NO_CONTENT)
