import logging
from http import HTTPStatus
from json.decoder import JSONDecodeError

from aiohttp.web import HTTPException, Request, Response, middleware
from pydantic.error_wrappers import ValidationError


log = logging.getLogger(__name__)


@middleware
async def error_middleware(request: Request, handler):
    try:
        response = await handler(request)
    except ValidationError as e:
        log.exception("Failed to verify request. Err: %r", e)
        return Response(
            status=HTTPStatus.BAD_REQUEST, text=f"Validate exception% {e}",
        )
    except JSONDecodeError as json_decode_error:
        log.exception(json_decode_error)
        return Response(
            status=HTTPStatus.BAD_REQUEST, text="JSONDecodeError",
        )
    except HTTPException:
        return Response(status=HTTPStatus.NOT_FOUND)
    except Exception:
        log.exception("Server error")
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return response
