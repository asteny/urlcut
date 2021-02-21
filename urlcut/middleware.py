import logging
from http import HTTPStatus
from json import dumps
from json.decoder import JSONDecodeError

from aiohttp.web import HTTPException, Request, Response, middleware
from pydantic import ValidationError


log = logging.getLogger(__name__)


@middleware
async def error_middleware(request: Request, handler):
    try:
        response = await handler(request)
    except ValidationError as e:
        log.exception("Failed to verify request. Err: %r", e)
        return Response(
            status=HTTPStatus.BAD_REQUEST,
            text=dumps({"error": "Validate exception", "exception": str(e)}),
        )
    except JSONDecodeError:
        log.exception("Failed to decode json")
        return Response(
            status=HTTPStatus.BAD_REQUEST,
            text=dumps({"error": "Failed to decode json"}),
        )
    except HTTPException:
        return Response(status=HTTPStatus.NOT_FOUND)
    except Exception:
        log.exception("Server error")
        return Response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            text=dumps({"error": "Internal server error"})
        )

    return response
