import logging
import os

from aiomisc import bind_socket, entrypoint
from aiomisc.log import LogFormat, LogLevel
from configargparse import ArgumentParser
from setproctitle import setproctitle
from yarl import URL

from urlcut.deps import setup_dependencies
from urlcut.services.rest import Rest


log = logging.getLogger(__name__)

parser = ArgumentParser(
    default_config_files=[os.path.join("/etc/urlcut/urlcut.conf")],
    auto_env_var_prefix="URLCUT_",
)

parser.add_argument("-D", "--debug", action="store_true")
parser.add_argument(
    "-s",
    "--pool-size",
    type=int,
    default=4,
    help="Thread pool size",
)

group = parser.add_argument_group("Logging options")
parser.add_argument(
    "-L",
    "--log-level",
    help="Log level",
    default="info",
    choices=LogLevel.choices(),
)

group.add_argument(
    "--log-format",
    choices=LogFormat.choices(),
    default="color",
)

group = parser.add_argument_group("Urlcut options")
group.add_argument(
    "--domain",
    required=True,
    type=URL,
    help="Domain name with protocol for generate short link and redirects \
    Example: https://example.com",
)

group.add_argument(
    "--alphabet",
    required=True,
    nargs="+",
    help="Alphabet for generating urls",
)

group.add_argument(
    "--salt",
    required=True,
    type=int,
    help="Salt for hide id",
)

group.add_argument(
    "--pepper",
    required=True,
    type=int,
    help="Pepper for hide id",
)

group.add_argument(
    "--address",
    type=str,
    default="::1",
    help="API listen HTTP address",
)
group.add_argument(
    "--port",
    type=int,
    default=8080,
    help="API listen HTTP port",
)

group = parser.add_argument_group("Postgres options")
group.add_argument("--pg-url", required=True, type=URL)
group.add_argument("--pg-min-pool-size", required=False, type=int, default=1)
group.add_argument("--pg-max-pool-size", required=False, type=int, default=10)


def main():
    args = parser.parse_args()
    os.environ.clear()

    setup_dependencies(args)

    socket = bind_socket(
        address=args.address,
        port=args.port,
        proto_name="http",
    )

    setproctitle("urlcut")

    services = [
        Rest(
            sock=socket,
            alphabet=args.alphabet,
            salt=args.salt,
            pepper=args.pepper,
            domain=args.domain,
        ),
    ]

    with entrypoint(
        *services,
        log_level=args.log_level,
        log_format=args.log_format,
        pool_size=args.pool_size,
        debug=args.debug,
    ) as loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
