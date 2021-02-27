import logging
from http import HTTPStatus
from json.decoder import JSONDecodeError

from aiohttp.web import HTTPException, Request, middleware
from aiohttp.web_response import json_response
from pydantic import ValidationError


log = logging.getLogger(__name__)


@middleware
async def error_middleware(request: Request, handler):
    try:
        response = await handler(request)
    except ValidationError as e:
        log.exception("Failed to verify request. Err: %r", e)
        return json_response(
            status=HTTPStatus.BAD_REQUEST,
            data={"error": "Validate exception", "exception": str(e)},
        )
    except JSONDecodeError:
        log.exception("Failed to decode json")
        return json_response(
            status=HTTPStatus.BAD_REQUEST,
            data={"error": "Failed to decode json"},
        )
    except HTTPException as e:
        return json_response(status=e.status, data={"error": e.text})
    except Exception:
        log.exception("Server error")
        return json_response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            data={"error": "Internal server error"},
        )

    return response
