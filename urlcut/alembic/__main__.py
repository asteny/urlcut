"""
Утилита для управления состоянием базы данных, обертка над alembic.
Можно вызывать из любой директории, а также указать произвольный DSN для базы
данных, отличный от указанного в файле alembic.ini.
"""
import argparse
import logging
import os

from urlcut.alembic_config import make_alembic_config

from alembic.config import CommandLine


def main():
    logging.basicConfig(level=logging.DEBUG)

    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    alembic.parser.add_argument(
        "--pg-url",
        default=os.getenv("URLCUT_PG_URL"),
        help="Database URL [env var: URLCUT_PG_URL]",
    )

    options = alembic.parser.parse_args()
    if "cmd" not in options:
        alembic.parser.error("too few arguments")
        exit(128)
    else:
        config = make_alembic_config(options)
        exit(alembic.run_cmd(config, options))


if __name__ == "__main__":
    main()
