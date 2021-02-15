import logging
from http import HTTPStatus
from json import JSONDecodeError

from aiohttp.web_response import Response, json_response
from pydantic.error_wrappers import ValidationError

from urlcut.handlers.base import Base
from urlcut.models.db import links_table
from urlcut.models.urls import UrlCreateData
from urlcut.utils.generate_link import (
    generate_link, generate_link_path, salted_number,
)


log = logging.getLogger(__name__)


class Urls(Base):
    async def post(self):
        try:
            data = await self.request.json()
            log.debug("Url data from post request is %r", data)

            parsed_url_data = UrlCreateData(**data)
            log.debug("Parsed url_data is %r", parsed_url_data)

            get_next_db_id = await self.db.fetchval(
                "SELECT NEXTVAL('links_id_seq')", column=0,
            )

            short_url_path = generate_link_path(
                self.alphabet,
                salted_number(
                    number=get_next_db_id,
                    salt=self.salt,
                    pepper=self.pepper,
                ),
            )
            log.debug("Short link path is %r", short_url_path)

            try:
                await self.db.fetchrow(
                    links_table.insert().values(
                        id=get_next_db_id,
                        name=parsed_url_data.name,
                        description=parsed_url_data.description,
                        long_url=parsed_url_data.url,
                        short_url_path=short_url_path,
                        not_active_after=parsed_url_data.notActiveAfter,
                        labels=parsed_url_data.labels,
                        creator=parsed_url_data.creator,
                        active=True,
                    ),
                )

                generated_link = generate_link(
                    domain=self.domain, short_path=short_url_path,
                )

                return json_response(
                    status=HTTPStatus.CREATED,
                    data={"link": str(generated_link)},

                )

            except Exception as e:
                log.exception(e)

                return Response(
                    status=HTTPStatus.SERVICE_UNAVAILABLE,
                )

        except (JSONDecodeError, ValidationError) as e:
            log.exception(e)
            return Response(status=HTTPStatus.BAD_REQUEST)

    async def delete(self):
        data = await self.request.json()
        log.debug("Delete data is %r", data)

        # TODO: write method
        return Response(status=HTTPStatus.NO_CONTENT)
